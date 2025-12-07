import os
from dotenv import load_dotenv
from urllib.parse import urlparse

# Carregar .env com override para garantir valores atualizados
env_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(env_path, override=True)


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")

    # Definir caminho do banco de dados na pasta instance
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    INSTANCE_PATH = os.path.join(BASE_DIR, "instance")
    DATABASE_PATH = os.path.join(INSTANCE_PATH, "propaganda.db")

    # Configurar Database URI de forma segura (evita problemas de encoding)
    db_uri_string = os.getenv("DATABASE_URI")

    if db_uri_string and db_uri_string.startswith("postgresql"):
        # Para PostgreSQL, parsear manualmente e passar parâmetros via connect_args
        # Isso evita problemas de encoding com mensagens de erro do PostgreSQL
        parsed = urlparse(db_uri_string)

        # URI mínima - apenas o driver
        SQLALCHEMY_DATABASE_URI = "postgresql://"

        # Passar TODOS os parâmetros via connect_args (bypass do parsing de string URI)
        SQLALCHEMY_ENGINE_OPTIONS = {
            "connect_args": {
                "host": parsed.hostname,
                "port": parsed.port or 5432,
                "dbname": parsed.path[1:] if parsed.path else "postgres",
                "user": parsed.username,
                "password": parsed.password,
                "connect_timeout": 10,
                "client_encoding": "UTF8",
                "application_name": "propaganda_system",
            },
            "pool_pre_ping": True,      # Verificar conexões antes de usar
            "pool_recycle": 3600,        # Reciclar conexões a cada hora
        }
    else:
        # SQLite ou outro banco
        SQLALCHEMY_DATABASE_URI = db_uri_string or f"sqlite:///{DATABASE_PATH}"
        SQLALCHEMY_ENGINE_OPTIONS = {}

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
