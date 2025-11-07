"""
Rotas principais do sistema
"""
from flask import Blueprint, jsonify, render_template

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Página inicial - API Info"""
    return jsonify({
        'message': 'Sistema de Propaganda API',
        'version': '2.0',
        'endpoints': {
            'api': '/api/*',
            'admin': '/admin/*',
            'cliente': '/cliente/*',
            'web_client': '/client'
        },
        'documentation': {
            'admin_login': '/admin/login',
            'cliente_register': '/cliente/register',
            'api_videos': '/api/videos?latitude=X&longitude=Y'
        }
    })


@main_bp.route('/client')
def client_web():
    """Interface web do cliente (visualizador)"""
    return render_template('client.html')
