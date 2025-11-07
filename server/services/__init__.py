"""
Camada de serviços - Lógica de negócio separada das rotas
"""
from .video_service import VideoService
from .cliente_service import ClienteService
from .auth_service import AuthService

__all__ = ['VideoService', 'ClienteService', 'AuthService']
