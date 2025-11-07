"""
Serviço para autenticação e autorização
"""

from flask import current_app
import hashlib


class AuthService:
    """Serviço para operações de autenticação"""

    @staticmethod
    def verificar_senha_admin(senha):
        """
        Verifica se a senha do admin está correta

        Args:
            senha: str

        Returns:
            bool
        """
        senha_correta = current_app.config["ADMIN_PASSWORD"]

        if senha == senha_correta:
            current_app.logger.info("Admin autenticado com sucesso")
            return True

        current_app.logger.warning("Tentativa de login admin falhou")
        return False

    @staticmethod
    def hash_password(password):
        """Gera hash SHA256 de uma senha"""
        return hashlib.sha256(password.encode()).hexdigest()

    @staticmethod
    def verify_password(password, hashed):
        """Verifica se a senha corresponde ao hash"""
        return AuthService.hash_password(password) == hashed
