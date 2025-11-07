from flask import Blueprint, request, jsonify, render_template, redirect, url_for, session, send_from_directory, flash
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash, generate_password_hash
from models import db, Video, SystemStatus, Cliente, LogVisualizacao
from forms import LoginForm, UploadVideoForm, ClienteLoginForm, ClienteRegisterForm, ClienteUploadVideoForm, AdicionarCreditosForm
from utils import get_videos_for_location
from config import Config
import os
from datetime import datetime

main_bp = Blueprint('main', __name__)
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')
api_bp = Blueprint('api', __name__, url_prefix='/api')
cliente_bp = Blueprint('cliente', __name__, url_prefix='/cliente')

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
    Apenas vídeos aprovados, pagos e não pausados
    Parâmetros: latitude, longitude
    """
    try:
        latitude = float(request.args.get('latitude'))
        longitude = float(request.args.get('longitude'))
    except (TypeError, ValueError):
        return jsonify({'error': 'Latitude e longitude são obrigatórios'}), 400
    
    # Filtrar apenas vídeos aprovados, pagos e não pausados
    all_videos = Video.query.filter_by(aprovado=True, pago=True, pausado=False).all()
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

@api_bp.route('/visualizacao/<int:video_id>', methods=['POST'])
def registrar_visualizacao(video_id):
    """
    Registra visualização de um vídeo e consome 1 crédito
    Parâmetros JSON: latitude, longitude (opcionais)
    """
    video = Video.query.get_or_404(video_id)
    
    # Verificar se o vídeo pode ser reproduzido
    if not video.aprovado or not video.pago or video.pausado:
        return jsonify({
            'error': 'Vídeo não disponível para reprodução',
            'pausado': video.pausado,
            'creditos': video.creditos
        }), 403
    
    # Consumir crédito
    if video.consumir_credito():
        # Criar log de visualização
        data = request.get_json() or {}
        log = LogVisualizacao(
            video_id=video_id,
            client_ip=request.remote_addr,
            client_latitude=data.get('latitude'),
            client_longitude=data.get('longitude')
        )
        db.session.add(log)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'creditos_restantes': video.creditos,
            'pausado': video.pausado,
            'visualizacoes_total': video.visualizacoes
        })
    else:
        return jsonify({
            'error': 'Sem créditos disponíveis',
            'creditos': video.creditos,
            'pausado': True
        }), 402

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

@admin_bp.route('/aprovar/<int:video_id>', methods=['POST'])
def aprovar_video(video_id):
    """Aprovar vídeo de cliente"""
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Não autorizado'}), 401
    
    video = Video.query.get_or_404(video_id)
    video.aprovado = True
    
    # Atualizar timestamp
    SystemStatus.update_timestamp()
    
    db.session.commit()
    
    flash(f'Vídeo "{video.original_filename}" aprovado com sucesso!', 'success')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/reprovar/<int:video_id>', methods=['POST'])
def reprovar_video(video_id):
    """Reprovar vídeo de cliente"""
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Não autorizado'}), 401
    
    video = Video.query.get_or_404(video_id)
    video.aprovado = False
    
    # Atualizar timestamp
    SystemStatus.update_timestamp()
    
    db.session.commit()
    
    flash(f'Vídeo "{video.original_filename}" reprovado!', 'warning')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/marcar-pago/<int:video_id>', methods=['POST'])
def marcar_pago(video_id):
    """Marcar vídeo como pago"""
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Não autorizado'}), 401
    
    video = Video.query.get_or_404(video_id)
    video.pago = True
    
    db.session.commit()
    
    flash(f'Vídeo "{video.original_filename}" marcado como pago!', 'success')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/adicionar-creditos/<int:video_id>', methods=['POST'])
def adicionar_creditos(video_id):
    """Adicionar créditos a um vídeo"""
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Não autorizado'}), 401
    
    video = Video.query.get_or_404(video_id)
    
    try:
        quantidade = int(request.form.get('creditos', 0))
        if quantidade > 0:
            video.adicionar_creditos(quantidade)
            db.session.commit()
            flash(f'{quantidade} crédito(s) adicionado(s) ao vídeo "{video.original_filename}"!', 'success')
        else:
            flash('Quantidade de créditos inválida!', 'danger')
    except ValueError:
        flash('Quantidade de créditos inválida!', 'danger')
    
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/pausar/<int:video_id>', methods=['POST'])
def pausar_video(video_id):
    """Pausar/Despausar vídeo"""
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Não autorizado'}), 401
    
    video = Video.query.get_or_404(video_id)
    video.pausado = not video.pausado
    
    db.session.commit()
    
    status = 'pausado' if video.pausado else 'despausado'
    flash(f'Vídeo "{video.original_filename}" {status}!', 'info')
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
            'client': '/client',
            'admin': '/admin'
        }
    })

@main_bp.route('/client')
def client_web():
    """Interface web do cliente"""
    return render_template('client.html')

# ==================== Portal do Cliente ====================

@cliente_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login do cliente"""
    if session.get('cliente_id'):
        return redirect(url_for('cliente.dashboard'))
    
    form = ClienteLoginForm()
    if form.validate_on_submit():
        cliente = Cliente.query.filter_by(email=form.email.data).first()
        if cliente and check_password_hash(cliente.senha, form.senha.data):
            session['cliente_id'] = cliente.id
            session['cliente_nome'] = cliente.nome
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('cliente.dashboard'))
        else:
            flash('Email ou senha incorretos!', 'danger')
    
    return render_template('cliente/login.html', form=form)

@cliente_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Cadastro de novo cliente"""
    if session.get('cliente_id'):
        return redirect(url_for('cliente.dashboard'))
    
    form = ClienteRegisterForm()
    if form.validate_on_submit():
        # Verificar se email já existe
        if Cliente.query.filter_by(email=form.email.data).first():
            flash('Email já cadastrado!', 'danger')
            return render_template('cliente/register.html', form=form)
        
        # Verificar se CPF/CNPJ já existe
        if form.cpf_cnpj.data and Cliente.query.filter_by(cpf_cnpj=form.cpf_cnpj.data).first():
            flash('CPF/CNPJ já cadastrado!', 'danger')
            return render_template('cliente/register.html', form=form)
        
        # Criar novo cliente
        cliente = Cliente(
            nome=form.nome.data,
            email=form.email.data,
            telefone=form.telefone.data,
            cpf_cnpj=form.cpf_cnpj.data,
            senha=generate_password_hash(form.senha.data)
        )
        db.session.add(cliente)
        db.session.commit()
        
        flash('Cadastro realizado com sucesso! Faça login para continuar.', 'success')
        return redirect(url_for('cliente.login'))
    
    return render_template('cliente/register.html', form=form)

@cliente_bp.route('/logout')
def logout():
    """Logout do cliente"""
    session.pop('cliente_id', None)
    session.pop('cliente_nome', None)
    flash('Logout realizado com sucesso!', 'info')
    return redirect(url_for('cliente.login'))

@cliente_bp.route('/dashboard')
def dashboard():
    """Dashboard do cliente"""
    if not session.get('cliente_id'):
        return redirect(url_for('cliente.login'))
    
    cliente = Cliente.query.get_or_404(session['cliente_id'])
    form = ClienteUploadVideoForm()
    videos = Video.query.filter_by(cliente_id=cliente.id).order_by(Video.uploaded_at.desc()).all()
    
    return render_template('cliente/dashboard.html', form=form, videos=videos, cliente=cliente)

@cliente_bp.route('/upload', methods=['POST'])
def upload_video():
    """Upload de vídeo pelo cliente"""
    if not session.get('cliente_id'):
        return jsonify({'error': 'Não autorizado'}), 401
    
    form = ClienteUploadVideoForm()
    if form.validate_on_submit():
        video_file = form.video.data
        filename = secure_filename(video_file.filename)
        
        # Gerar nome único
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{timestamp}_{filename}"
        filepath = os.path.join(Config.UPLOAD_FOLDER, unique_filename)
        
        # Salvar arquivo
        video_file.save(filepath)
        
        # Criar registro no banco (pendente de aprovação)
        new_video = Video(
            filename=unique_filename,
            original_filename=filename,
            latitude=form.latitude.data,
            longitude=form.longitude.data,
            radius_km=form.radius_km.data,
            cliente_id=session['cliente_id'],
            aprovado=False,  # Aguardando aprovação
            pago=False,
            creditos=0,
            pausado=True  # Pausado até aprovação e pagamento
        )
        db.session.add(new_video)
        db.session.commit()
        
        flash(f'Vídeo "{filename}" enviado com sucesso! Aguardando aprovação do admin.', 'success')
        return redirect(url_for('cliente.dashboard'))
    
    # Se houver erros de validação
    for field, errors in form.errors.items():
        for error in errors:
            flash(f'{field}: {error}', 'danger')
    
    return redirect(url_for('cliente.dashboard'))

@cliente_bp.route('/video/<int:video_id>/stats')
def video_stats():
    """Estatísticas de um vídeo"""
    if not session.get('cliente_id'):
        return redirect(url_for('cliente.login'))
    
    video = Video.query.get_or_404(video_id)
    
    # Verificar se o vídeo pertence ao cliente
    if video.cliente_id != session['cliente_id']:
        flash('Acesso negado!', 'danger')
        return redirect(url_for('cliente.dashboard'))
    
    # Buscar logs de visualização
    logs = LogVisualizacao.query.filter_by(video_id=video_id).order_by(LogVisualizacao.visualizado_em.desc()).limit(100).all()
    
    return render_template('cliente/video_stats.html', video=video, logs=logs)

