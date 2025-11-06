import os
from dotenv import load_dotenv

load_dotenv()


class ClientConfig:
    # URL do servidor
    SERVER_URL = os.getenv("SERVER_URL", "http://10.13.24.80:5050")

    # Localização do cliente (configurar de acordo com a localização real)
    # Exemplo: São Paulo, Brasil
    CLIENT_LATITUDE = float(os.getenv("CLIENT_LATITUDE", "-23"))
    CLIENT_LONGITUDE = float(os.getenv("CLIENT_LONGITUDE", "-46"))

    # Intervalo de verificação de atualizações (em segundos)
    CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "300"))  # 5 minutos

    # Pasta para salvar vídeos baixados
    DOWNLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "videos")
    os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

    # Arquivo para armazenar o último timestamp
    TIMESTAMP_FILE = os.path.join(os.path.dirname(__file__), "last_timestamp.txt")
