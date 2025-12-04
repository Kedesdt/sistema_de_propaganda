"""
Rotas do portal do cliente
"""
from flask import Blueprint, request, render_template, redirect, url_for, session, flash
from models import db
from forms import ClienteLoginForm, ClienteRegisterForm, ClienteUploadVideoForm
from utils.decorators import cliente_required
from services import ClienteService, VideoService

cliente_bp = Blueprint('cliente', __name__, url_prefix='/cliente')


@cliente_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login do cliente"""
    if session.get('cliente_id'):
        return redirect(url_for('cliente.dashboard'))
    
    form = ClienteLoginForm()
    if form.validate_on_submit():
        cliente = ClienteService.autenticar_cliente(form.email.data, form.senha.data)
        if cliente:
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
    
    # Debug: Log dados recebidos do POST
    if request.method == 'POST':
        from flask import current_app
        current_app.logger.info(f'POST data recebido: {dict(request.form)}')
        current_app.logger.info(f'Form data após parse: nome={form.nome.data}, email={form.email.data}, endereco={form.endereco.data}')
    
    # Debug: Log erros de validação
    if request.method == 'POST' and not form.validate_on_submit():
        from flask import current_app
        current_app.logger.warning(f'Erros de validação no registro: {form.errors}')
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{field}: {error}', 'danger')
    
    if form.validate_on_submit():
        cliente, error = ClienteService.registrar_cliente(
            nome=form.nome.data,
            email=form.email.data,
            senha=form.senha.data,
            cpf_cnpj=form.cpf_cnpj.data,
            telefone=form.telefone.data,
            endereco=form.endereco.data
        )
        
        if cliente:
            flash('Cadastro realizado com sucesso! Faça login para continuar.', 'success')
            return redirect(url_for('cliente.login'))
        else:
            flash(f'Erro: {error}', 'danger')
            return render_template('cliente/register.html', form=form)
    
    return render_template('cliente/register.html', form=form)


@cliente_bp.route('/logout')
def logout():
    """Logout do cliente"""
    session.pop('cliente_id', None)
    session.pop('cliente_nome', None)
    flash('Logout realizado com sucesso!', 'info')
    return redirect(url_for('cliente.login'))


@cliente_bp.route('/dashboard')
@cliente_required
def dashboard():
    """Dashboard do cliente"""
    cliente = ClienteService.get_cliente_by_id(session['cliente_id'])
    if not cliente:
        flash('Cliente não encontrado!', 'danger')
        return redirect(url_for('cliente.login'))
    
    form = ClienteUploadVideoForm()
    stats = ClienteService.get_dashboard_stats(cliente.id)
    
    return render_template('cliente/dashboard.html', form=form, videos=stats['videos'], cliente=cliente, stats=stats)


@cliente_bp.route('/upload', methods=['POST'])
@cliente_required
def upload_video():
    """Upload de vídeo pelo cliente"""
    form = ClienteUploadVideoForm()
    if form.validate_on_submit():
        video, error = VideoService.upload_video(
            file=form.video.data,
            latitude=form.latitude.data,
            longitude=form.longitude.data,
            radius_km=form.radius_km.data,
            cliente_id=session['cliente_id']
        )
        
        if video:
            flash(f'Vídeo "{video.filename}" enviado com sucesso! Aguardando aprovação do admin.', 'success')
        else:
            flash(f'Erro: {error}', 'danger')
        
        return redirect(url_for('cliente.dashboard'))
    
    # Se houver erros de validação
    for field, errors in form.errors.items():
        for error in errors:
            flash(f'{field}: {error}', 'danger')
    
    return redirect(url_for('cliente.dashboard'))


@cliente_bp.route('/video/<int:video_id>/stats')
@cliente_required
def video_stats(video_id):
    """Estatísticas de um vídeo"""
    stats = ClienteService.get_estatisticas_video(video_id, session['cliente_id'])
    
    if not stats:
        flash('Vídeo não encontrado ou acesso negado!', 'danger')
        return redirect(url_for('cliente.dashboard'))
    
    return render_template('cliente/video_stats.html', video=stats['video'], logs=stats['visualizacoes'], stats=stats)
