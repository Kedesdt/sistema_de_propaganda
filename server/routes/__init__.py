"""
Módulo de rotas do sistema de propaganda
Organizado em blueprints separados por funcionalidade
"""
from .main import main_bp
from .api import api_bp
from .admin import admin_bp
from .cliente import cliente_bp

__all__ = ['main_bp', 'api_bp', 'admin_bp', 'cliente_bp']
