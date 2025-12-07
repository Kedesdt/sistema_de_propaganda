"""
Decorators para autenticação e autorização
"""
from functools import wraps
from flask import session, redirect, url_for, flash, jsonify


def admin_required(f):
    """
    Decorator que requer autenticação de admin.
    Redireciona para login se não autenticado.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            flash('Você precisa estar logado como admin para acessar esta página.', 'warning')
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated_function


def cliente_required(f):
    """
    Decorator que requer autenticação de cliente.
    Redireciona para login se não autenticado.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        cliente_id = session.get('cliente_id')
        # DEBUG TEMPORÁRIO
        from flask import current_app
        current_app.logger.warning(f'[DEBUG] @cliente_required - session.get(cliente_id) = {cliente_id!r} (type: {type(cliente_id).__name__})')
        current_app.logger.warning(f'[DEBUG] @cliente_required - bool(cliente_id) = {bool(cliente_id)}')
        current_app.logger.warning(f'[DEBUG] @cliente_required - session completa = {dict(session)}')
        
        if not session.get('cliente_id'):
            flash('Você precisa estar logado para acessar esta página.', 'warning')
            return redirect(url_for('cliente.login'))
        return f(*args, **kwargs)
    return decorated_function


def api_auth_required(f):
    """
    Decorator para rotas de API que requer autenticação.
    Retorna JSON 401 se não autenticado.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Verificar se é admin ou cliente
        if not session.get('admin_logged_in') and not session.get('cliente_id'):
            return jsonify({'error': 'Não autorizado'}), 401
        return f(*args, **kwargs)
    return decorated_function


def admin_or_owner_required(f):
    """
    Decorator que permite acesso se for admin OU dono do recurso.
    Útil para rotas onde o cliente pode acessar seus próprios recursos.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Admin sempre tem acesso
        if session.get('admin_logged_in'):
            return f(*args, **kwargs)
        
        # Cliente precisa estar logado
        if not session.get('cliente_id'):
            flash('Você precisa estar logado para acessar esta página.', 'warning')
            return redirect(url_for('cliente.login'))
        
        return f(*args, **kwargs)
    return decorated_function
