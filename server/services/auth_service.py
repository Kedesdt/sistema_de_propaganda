"""
Serviço para autenticação e autorização
"""

from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash


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
        """
        Gera hash seguro de uma senha usando pbkdf2:sha256
        
        NOTA: Use este método para armazenar senhas de forma segura.
        NÃO use SHA256 simples para senhas!
        
        Args:
            password: str - Senha em texto plano
            
        Returns:
            str - Hash seguro da senha (pbkdf2:sha256 com salt)
        """
        return generate_password_hash(password, method='pbkdf2:sha256')

    @staticmethod
    def verify_password(password, hashed):
        """
        Verifica se a senha corresponde ao hash
        
        Args:
            password: str - Senha em texto plano
            hashed: str - Hash armazenado (pbkdf2:sha256)
            
        Returns:
            bool - True se a senha está correta
        """
        return check_password_hash(hashed, password)
