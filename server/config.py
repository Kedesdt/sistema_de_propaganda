import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    
    # Definir caminho do banco de dados na pasta instance
    # Flask cria automaticamente a pasta instance/
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    INSTANCE_PATH = os.path.join(BASE_DIR, 'instance')
    DATABASE_PATH = os.path.join(INSTANCE_PATH, 'propaganda.db')
    
    # Se DATABASE_URI não estiver no .env, usar o caminho da instance
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URI", 
        f"sqlite:///{DATABASE_PATH}"
    )
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(
        os.path.dirname(__file__), os.getenv("UPLOAD_FOLDER", "uploads")
    )
    MAX_CONTENT_LENGTH = 500 * 1024 * 1024  # 500 MB max file size
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")
    PORT = int(os.getenv("PORT", "5000"))

    # Criar pastas se não existirem
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(INSTANCE_PATH, exist_ok=True)
