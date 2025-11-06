import requests
import cv2
import os
import time
from datetime import datetime
from config import ClientConfig
import time


class PropagandaClient:
    def __init__(self):
        self.config = ClientConfig()
        self.last_timestamp = self.load_last_timestamp()
        self.current_videos = []

    def load_last_timestamp(self):
        """Carrega o último timestamp salvo"""
        if os.path.exists(self.config.TIMESTAMP_FILE):
            with open(self.config.TIMESTAMP_FILE, "r") as f:
                return f.read().strip()
        return None

    def save_last_timestamp(self, timestamp):
        """Salva o timestamp atual"""
        with open(self.config.TIMESTAMP_FILE, "w") as f:
            f.write(timestamp)
        self.last_timestamp = timestamp

    def check_for_updates(self):
        """Verifica se há atualizações no servidor"""
        try:
            response = requests.get(
                f"{self.config.SERVER_URL}/api/timestamp", timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                server_timestamp = data["last_update"]

                if self.last_timestamp != server_timestamp:
                    print(
                        f"[{datetime.now().strftime('%H:%M:%S')}] Nova atualização detectada!"
                    )
                    return True, server_timestamp
                else:
                    print(
                        f"[{datetime.now().strftime('%H:%M:%S')}] Nenhuma atualização disponível."
                    )
                    return False, server_timestamp
        except Exception as e:
            print(f"[ERRO] Falha ao verificar atualizações: {e}")
            return False, None

    def get_available_videos(self):
        """Busca vídeos disponíveis para a localização do cliente"""
        try:
            params = {
                "latitude": self.config.CLIENT_LATITUDE,
                "longitude": self.config.CLIENT_LONGITUDE,
            }
            response = requests.get(
                f"{self.config.SERVER_URL}/api/videos", params=params, timeout=10
            )
            print(f"{self.config.SERVER_URL}/api/videos", params)
            if response.status_code == 200:
                data = response.json()
                return data["videos"]
            else:
                print(f"[ERRO] Falha ao buscar vídeos: {response.status_code}")
                return []
        except Exception as e:
            print(f"[ERRO] Falha ao buscar vídeos: {e}")
            return []

    def download_video(self, video_info):
        """Baixa um vídeo do servidor"""
        try:
            video_id = video_info["id"]
            filename = video_info["filename"]
            filepath = os.path.join(self.config.DOWNLOAD_FOLDER, filename)

            # Não baixar se já existe
            if os.path.exists(filepath):
                print(f"  - Vídeo já existe: {video_info['original_filename']}")
                return filepath

            print(f"  - Baixando: {video_info['original_filename']}...", end=" ")
            response = requests.get(
                f"{self.config.SERVER_URL}/api/download/{video_id}",
                stream=True,
                timeout=30,
            )

            if response.status_code == 200:
                with open(filepath, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                print("OK")
                return filepath
            else:
                print(f"ERRO ({response.status_code})")
                return None
        except Exception as e:
            print(f"ERRO: {e}")
            return None

    def update_videos(self):
        """Atualiza a lista de vídeos"""
        print(
            f"\n[{datetime.now().strftime('%H:%M:%S')}] Atualizando lista de vídeos..."
        )

        # Limpar pasta de vídeos antigos
        if os.path.exists(self.config.DOWNLOAD_FOLDER):
            for file in os.listdir(self.config.DOWNLOAD_FOLDER):
                filepath = os.path.join(self.config.DOWNLOAD_FOLDER, file)
                try:
                    os.remove(filepath)
                    print(f"  - Removido: {file}")
                except Exception as e:
                    print(f"  - Erro ao remover {file}: {e}")

        # Buscar vídeos disponíveis
        videos = self.get_available_videos()
        print(f"  - {len(videos)} vídeo(s) disponível(is) para sua localização")

        # Baixar vídeos
        self.current_videos = []
        for video in videos:
            filepath = self.download_video(video)
            if filepath:
                self.current_videos.append(filepath)

        print(f"  - Total de vídeos baixados: {len(self.current_videos)}")

        if self.current_videos:
            print(f"\n[INFO] Vídeos prontos para reprodução!")
        else:
            print(f"\n[AVISO] Nenhum vídeo disponível para sua localização.")

    def play_videos(self):
        """Reproduz os vídeos em loop fullscreen"""
        if not self.current_videos:
            print("[INFO] Nenhum vídeo para reproduzir. Aguardando...")
            time.sleep(10)
            return

        print(
            f"\n[{datetime.now().strftime('%H:%M:%S')}] Reproduzindo {len(self.current_videos)} vídeo(s) em loop..."
        )
        print("[INFO] Pressione 'q' para sair ou 's' para pular o vídeo")

        while True:
            for video_path in self.current_videos:
                cap = cv2.VideoCapture(video_path)

                if not cap.isOpened():
                    print(f"[ERRO] Não foi possível abrir: {video_path}")
                    continue

                # Configurar janela fullscreen
                window_name = "Propaganda"
                cv2.namedWindow(window_name, cv2.WND_PROP_FULLSCREEN)
                cv2.setWindowProperty(
                    window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN
                )

                fps = cap.get(cv2.CAP_PROP_FPS)
                if fps == 0:
                    fps = 30
                delay = int(1000 / fps)

                while cap.isOpened():
                    ret, frame = cap.read()

                    if not ret:
                        break

                    cv2.imshow(window_name, frame)

                    key = cv2.waitKey(delay) & 0xFF
                    if key == ord("q"):  # Sair
                        cap.release()
                        cv2.destroyAllWindows()
                        return False
                    elif key == ord("s"):  # Pular vídeo
                        break

                cap.release()
                cv2.destroyAllWindows()

            # Pequena pausa entre loops
            time.sleep(0.5)

        return True

    def run(self):
        """Loop principal do cliente"""
        print("=" * 60)
        print("SISTEMA DE PROPAGANDA - CLIENTE")
        print("=" * 60)
        print(f"Servidor: {self.config.SERVER_URL}")
        print(
            f"Localização: Lat {self.config.CLIENT_LATITUDE}, Lon {self.config.CLIENT_LONGITUDE}"
        )
        print(f"Intervalo de verificação: {self.config.CHECK_INTERVAL} segundos")
        print("=" * 60)

        # Primeira atualização
        self.update_videos()
        check_result = self.check_for_updates()
        if check_result:
            has_update, new_timestamp = check_result
            if new_timestamp:
                self.save_last_timestamp(new_timestamp)

        last_check = time.time()

        try:
            while True:
                # Verificar se é hora de checar atualizações
                current_time = time.time()
                if current_time - last_check >= self.config.CHECK_INTERVAL:
                    check_result = self.check_for_updates()

                    if check_result:
                        has_update, new_timestamp = check_result
                        if has_update and new_timestamp:
                            self.save_last_timestamp(new_timestamp)
                            self.update_videos()

                    last_check = current_time

                # Reproduzir vídeos
                continue_playing = self.play_videos()
                if not continue_playing:
                    break

        except KeyboardInterrupt:
            print("\n\n[INFO] Encerrando cliente...")
        finally:
            cv2.destroyAllWindows()


if __name__ == "__main__":
    while True:
        try:
            client = PropagandaClient()
            client.run()
        except Exception as e:
            print(f"[ERRO] Ocorreu um erro: {e}")

        time.sleep(5)
