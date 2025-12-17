"""
Rotas administrativas
"""
from flask import Blueprint, request, render_template, redirect, url_for, session, send_from_directory, send_file, flash, current_app
from models import db, SystemStatus
from forms import LoginForm, UploadVideoForm
from utils.decorators import admin_required
from services import VideoService, AuthService
import os
import zipfile
import tempfile
import shutil

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login do admin"""
    if session.get('admin_logged_in'):
        return redirect(url_for('admin.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        if AuthService.verificar_senha_admin(form.password.data):
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
@admin_required
def dashboard():
    """Dashboard do admin"""
    form = UploadVideoForm()
    videos = VideoService.get_all_videos()
    last_update = SystemStatus.get_last_update()
    
    return render_template('admin.html', form=form, videos=videos, last_update=last_update)


@admin_bp.route('/upload', methods=['POST'])
@admin_required
def upload_video():
    """Upload de novo vídeo"""
    form = UploadVideoForm()
    if form.validate_on_submit():
        video, error = VideoService.upload_video(
            file=form.video.data,
            latitude=form.latitude.data,
            longitude=form.longitude.data,
            radius_km=form.radius_km.data,
            cliente_id=None  # Admin não tem cliente_id
        )
        
        if video:
            # Atualizar timestamp
            SystemStatus.update_timestamp()
            db.session.commit()
            
            flash(f'Vídeo "{video.filename}" enviado com sucesso!', 'success')
        else:
            flash(f'Erro: {error}', 'danger')
        
        return redirect(url_for('admin.dashboard'))
    
    # Se houver erros de validação
    for field, errors in form.errors.items():
        for error in errors:
            flash(f'{field}: {error}', 'danger')
    
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/aprovar/<int:video_id>', methods=['POST'])
@admin_required
def aprovar_video(video_id):
    """Aprovar vídeo de cliente"""
    success, message = VideoService.aprovar_video(video_id)
    
    if success:
        # Atualizar timestamp
        SystemStatus.update_timestamp()
        db.session.commit()
        flash(message, 'success')
    else:
        flash(message, 'danger')
    
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/reprovar/<int:video_id>', methods=['POST'])
@admin_required
def reprovar_video(video_id):
    """Reprovar vídeo de cliente"""
    success, message = VideoService.reprovar_video(video_id)
    
    if success:
        # Atualizar timestamp
        SystemStatus.update_timestamp()
        db.session.commit()
        flash(message, 'warning')
    else:
        flash(message, 'danger')
    
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/marcar-pago/<int:video_id>', methods=['POST'])
@admin_required
def marcar_pago(video_id):
    """Marcar vídeo como pago/não pago"""
    success, message = VideoService.marcar_como_pago(video_id)
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'danger')
    
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/adicionar-creditos/<int:video_id>', methods=['POST'])
@admin_required
def adicionar_creditos(video_id):
    """Adicionar créditos a um vídeo"""
    try:
        quantidade = int(request.form.get('creditos', 0))
        success, message = VideoService.adicionar_creditos(video_id, quantidade)
        
        if success:
            flash(message, 'success')
        else:
            flash(message, 'danger')
    except ValueError:
        flash('Quantidade de créditos inválida!', 'danger')
    
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/pausar/<int:video_id>', methods=['POST'])
@admin_required
def pausar_video(video_id):
    """Pausar/Despausar vídeo"""
    success, message = VideoService.pausar_video(video_id)
    
    if success:
        flash(message, 'info')
    else:
        flash(message, 'danger')
    
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/delete/<int:video_id>', methods=['POST'])
@admin_required
def delete_video(video_id):
    """Deletar vídeo"""
    success, message = VideoService.deletar_video(video_id)
    
    if success:
        # Atualizar timestamp
        SystemStatus.update_timestamp()
        db.session.commit()
        flash(message, 'success')
    else:
        flash(message, 'danger')
    
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/download-client')
@admin_required
def download_client():
    """Download da pasta client compactada"""
    try:
        # Localizar pasta client (um nível acima da pasta server)
        server_folder = os.path.dirname(os.path.dirname(__file__))
        project_root = os.path.dirname(server_folder)
        client_folder = os.path.join(project_root, 'client')
        
        if not os.path.exists(client_folder):
            flash('Pasta client/ não encontrada!', 'danger')
            return redirect(url_for('admin.dashboard'))
        
        # Criar arquivo ZIP temporário
        temp_dir = tempfile.gettempdir()
        zip_path = os.path.join(temp_dir, 'propaganda_client.zip')
        
        # Remover ZIP antigo se existir
        if os.path.exists(zip_path):
            os.remove(zip_path)
        
        # Criar ZIP com todos os arquivos da pasta client
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(client_folder):
                # Ignorar pastas de ambiente virtual e cache
                dirs[:] = [d for d in dirs if d not in ['venv', '__pycache__', '.pytest_cache', 'downloads']]
                
                for file in files:
                    # Ignorar arquivos desnecessários
                    if file.endswith(('.pyc', '.pyo', '.exe', '.timestamp')):
                        continue
                    
                    file_path = os.path.join(root, file)
                    # Nome do arquivo no ZIP (relativo à pasta client)
                    arcname = os.path.join('client', os.path.relpath(file_path, client_folder))
                    zipf.write(file_path, arcname)
        
        # Enviar arquivo ZIP
        return send_file(
            zip_path,
            as_attachment=True,
            download_name='propaganda_client.zip',
            mimetype='application/zip'
        )
        
    except Exception as e:
        current_app.logger.error(f"Erro ao criar ZIP do client: {e}")
        flash(f'Erro ao preparar download: {str(e)}', 'danger')
        return redirect(url_for('admin.dashboard'))
