import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI", "sqlite:///propaganda.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(
        os.path.dirname(__file__), os.getenv("UPLOAD_FOLDER", "uploads")
    )
    MAX_CONTENT_LENGTH = 500 * 1024 * 1024  # 500 MB max file size
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")
    PORT = int(os.getenv("PORT", "5000"))

    # Criar pasta de uploads se não existir
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
