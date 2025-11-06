from flask import Blueprint, request, jsonify, render_template, redirect, url_for, session, send_from_directory, flash
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash, generate_password_hash
from models import db, Video, SystemStatus
from forms import LoginForm, UploadVideoForm
from utils import get_videos_for_location
from config import Config
import os
from datetime import datetime

main_bp = Blueprint('main', __name__)
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')
api_bp = Blueprint('api', __name__, url_prefix='/api')

# ==================== API Routes ====================

@api_bp.route('/timestamp', methods=['GET'])
def get_timestamp():
    """Retorna o timestamp da última atualização"""
    last_update = SystemStatus.get_last_update()
    return jsonify({
        'last_update': last_update.isoformat(),
        'timestamp': int(last_update.timestamp())
    })

@api_bp.route('/videos', methods=['GET'])
def get_videos():
    """
    Retorna lista de vídeos disponíveis para a localização do cliente
    Parâmetros: latitude, longitude
    """
    try:
        latitude = float(request.args.get('latitude'))
        longitude = float(request.args.get('longitude'))
    except (TypeError, ValueError):
        return jsonify({'error': 'Latitude e longitude são obrigatórios'}), 400
    
    all_videos = Video.query.all()
    available_videos = get_videos_for_location(all_videos, latitude, longitude)
    
    return jsonify({
        'videos': [video.to_dict() for video in available_videos],
        'count': len(available_videos)
    })

@api_bp.route('/download/<int:video_id>', methods=['GET'])
def download_video(video_id):
    """Baixa um vídeo específico"""
    video = Video.query.get_or_404(video_id)
    return send_from_directory(
        Config.UPLOAD_FOLDER,
        video.filename,
        as_attachment=True,
        download_name=video.original_filename
    )

# ==================== Admin Routes ====================

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login do admin"""
    if session.get('admin_logged_in'):
        return redirect(url_for('admin.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        if form.password.data == Config.ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Senha incorreta!', 'danger')
    
    return render_template('login.html', form=form)

@admin_bp.route('/logout')
def logout():
    """Logout do admin"""
    session.pop('admin_logged_in', None)
    flash('Logout realizado com sucesso!', 'info')
    return redirect(url_for('admin.login'))

@admin_bp.route('/')
def dashboard():
    """Dashboard do admin"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))
    
    form = UploadVideoForm()
    videos = Video.query.order_by(Video.uploaded_at.desc()).all()
    last_update = SystemStatus.get_last_update()
    
    return render_template('admin.html', form=form, videos=videos, last_update=last_update)

@admin_bp.route('/upload', methods=['POST'])
def upload_video():
    """Upload de novo vídeo"""
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Não autorizado'}), 401
    
    form = UploadVideoForm()
    if form.validate_on_submit():
        video_file = form.video.data
        filename = secure_filename(video_file.filename)
        
        # Gerar nome único
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{timestamp}_{filename}"
        filepath = os.path.join(Config.UPLOAD_FOLDER, unique_filename)
        
        # Salvar arquivo
        video_file.save(filepath)
        
        # Criar registro no banco
        new_video = Video(
            filename=unique_filename,
            original_filename=filename,
            latitude=form.latitude.data,
            longitude=form.longitude.data,
            radius_km=form.radius_km.data
        )
        db.session.add(new_video)
        
        # Atualizar timestamp
        SystemStatus.update_timestamp()
        
        db.session.commit()
        
        flash(f'Vídeo "{filename}" enviado com sucesso!', 'success')
        return redirect(url_for('admin.dashboard'))
    
    # Se houver erros de validação
    for field, errors in form.errors.items():
        for error in errors:
            flash(f'{field}: {error}', 'danger')
    
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/delete/<int:video_id>', methods=['POST'])
def delete_video(video_id):
    """Deletar vídeo"""
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Não autorizado'}), 401
    
    video = Video.query.get_or_404(video_id)
    
    # Deletar arquivo físico
    filepath = os.path.join(Config.UPLOAD_FOLDER, video.filename)
    if os.path.exists(filepath):
        os.remove(filepath)
    
    # Deletar registro do banco
    db.session.delete(video)
    
    # Atualizar timestamp
    SystemStatus.update_timestamp()
    
    db.session.commit()
    
    flash(f'Vídeo "{video.original_filename}" deletado com sucesso!', 'success')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/download-client')
def download_client():
    """Download do client.exe"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))
    
    client_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'client')
    client_exe = 'client.exe'
    
    if os.path.exists(os.path.join(client_folder, client_exe)):
        return send_from_directory(
            client_folder,
            client_exe,
            as_attachment=True,
            download_name='propaganda_client.exe'
        )
    else:
        flash('Arquivo client.exe não encontrado na pasta client/', 'danger')
        return redirect(url_for('admin.dashboard'))

# ==================== Main Routes ====================

@main_bp.route('/')
def index():
    """Página inicial"""
    return jsonify({
        'message': 'Sistema de Propaganda API',
        'version': '1.0',
        'endpoints': {
            'timestamp': '/api/timestamp',
            'videos': '/api/videos?latitude=<lat>&longitude=<lon>',
            'download': '/api/download/<video_id>',
            'admin': '/admin'
        }
    })
