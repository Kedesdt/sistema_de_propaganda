import requests
import cv2
import os
import time
from datetime import datetime
from config import ClientConfig
import sys
from PIL import Image
import numpy as np


class PropagandaClient:
    def __init__(self, url=None):
        self.config = ClientConfig()
        self.last_timestamp = self.load_last_timestamp()
        self.current_media = []  # Vídeos e imagens
        self.downloaded_media = []  # Lista com informações sobre cada mídia
        if url:
            self.config.SERVER_URL = url
        
        # Constantes
        self.IMAGE_DISPLAY_DURATION = 30  # 30 segundos para imagens

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
        """Busca mídias (vídeos e imagens) disponíveis para a localização do cliente"""
        try:
            params = {
                "latitude": self.config.CLIENT_LATITUDE,
                "longitude": self.config.CLIENT_LONGITUDE,
            }
            response = requests.get(
                f"{self.config.SERVER_URL}/api/videos", params=params, timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                return data["videos"]
            else:
                print(f"[ERRO] Falha ao buscar mídias: {response.status_code}")
                return []
        except Exception as e:
            print(f"[ERRO] Falha ao buscar mídias: {e}")
            return []

    def is_image(self, filename):
        """Verifica se o arquivo é uma imagem"""
        image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.webp')
        return filename.lower().endswith(image_extensions)
    
    def download_media(self, media_info):
        """Baixa uma mídia (vídeo ou imagem) do servidor"""
        try:
            media_id = media_info["id"]
            filename = media_info["filename"]
            filepath = os.path.join(self.config.DOWNLOAD_FOLDER, filename)
            original_name = media_info['original_filename']
            is_image = self.is_image(original_name)
            media_type = "Imagem" if is_image else "Vídeo"

            # Não baixar se já existe
            if os.path.exists(filepath):
                print(f"  - {media_type} já existe: {original_name}")
                return filepath, is_image, media_id

            print(f"  - Baixando {media_type}: {original_name}...", end=" ")
            response = requests.get(
                f"{self.config.SERVER_URL}/api/download/{media_id}",
                stream=True,
                timeout=30,
            )

            if response.status_code == 200:
                with open(filepath, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                print("OK")
                return filepath, is_image, media_id
            else:
                print(f"ERRO ({response.status_code})")
                return None, None, None
        except Exception as e:
            print(f"ERRO: {e}")
            return None, None, None

    def register_visualization(self, media_id):
        """Registra uma impressão no servidor"""
        try:
            response = requests.post(
                f"{self.config.SERVER_URL}/api/visualizacao/{media_id}",
                json={
                    "latitude": self.config.CLIENT_LATITUDE,
                    "longitude": self.config.CLIENT_LONGITUDE
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"  📊 Impressão registrada - Créditos restantes: {data['creditos_restantes']}")
            else:
                print(f"  ⚠️ Falha ao registrar impressão: {response.status_code}")
        except Exception as e:
            print(f"  ⚠️ Erro ao registrar impressão: {e}")
    
    def update_videos(self):
        """Atualiza a lista de mídias (vídeos e imagens)"""
        print(
            f"\n[{datetime.now().strftime('%H:%M:%S')}] Atualizando lista de mídias..."
        )

        # Buscar mídias disponíveis
        media_list = self.get_available_videos()
        print(f"  - {len(media_list)} mídia(s) disponível(is) para sua localização")
        
        if len(media_list) == 0:
            # Limpar tudo se não há mídias
            if os.path.exists(self.config.DOWNLOAD_FOLDER):
                for file in os.listdir(self.config.DOWNLOAD_FOLDER):
                    filepath = os.path.join(self.config.DOWNLOAD_FOLDER, file)
                    try:
                        os.remove(filepath)
                        print(f"  - Removido: {file}")
                    except Exception as e:
                        print(f"  - Erro ao remover {file}: {e}")
            
            self.current_media = []
            self.downloaded_media = []
            print(f"\n[AVISO] Nenhuma mídia disponível para sua localização.")
            return
        
        # Verificar mudanças na lista
        new_ids = set(m["id"] for m in media_list)
        current_ids = set(m["id"] for m in self.downloaded_media)
        
        # Identificar mídias removidas
        removed_ids = current_ids - new_ids
        if removed_ids:
            print(f"  🗑️ Removendo {len(removed_ids)} mídia(s) antiga(s)...")
            for media_info in self.downloaded_media[:]:
                if media_info["id"] in removed_ids:
                    filepath = media_info["path"]
                    if os.path.exists(filepath):
                        try:
                            os.remove(filepath)
                            print(f"    ✅ Removido: {media_info['filename']}")
                        except Exception as e:
                            print(f"    ❌ Erro ao remover {media_info['filename']}: {e}")
                    self.downloaded_media.remove(media_info)
        
        # Identificar mídias novas
        new_media_ids = new_ids - current_ids
        if new_media_ids:
            print(f"  📥 Baixando {len(new_media_ids)} mídia(s) nova(s)...")
            for media in media_list:
                if media["id"] in new_media_ids:
                    filepath, is_image, media_id = self.download_media(media)
                    if filepath:
                        self.downloaded_media.append({
                            "id": media_id,
                            "path": filepath,
                            "filename": media["original_filename"],
                            "is_image": is_image
                        })
        
        # Atualizar lista de caminhos para reprodução
        self.current_media = [m["path"] for m in self.downloaded_media]
        
        print(f"  - Total de mídias prontas: {len(self.current_media)}")

        if self.current_media:
            print(f"\n[INFO] Mídias prontas para reprodução!")
        else:
            print(f"\n[AVISO] Nenhuma mídia disponível para sua localização.")

    def display_image(self, image_path, media_info, window_name):
        """Exibe uma imagem por 30 segundos"""
        try:
            # Carregar imagem usando PIL
            pil_image = Image.open(image_path)
            
            # Converter para RGB se necessário
            if pil_image.mode != 'RGB':
                pil_image = pil_image.convert('RGB')
            
            # Converter para numpy array (formato BGR para OpenCV)
            image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
            
            # Obter dimensões da tela
            screen_height, screen_width = image.shape[:2]
            
            print(f"  ▶️ Exibindo imagem: {media_info['filename']} por {self.IMAGE_DISPLAY_DURATION}s")
            
            # Registrar impressão
            self.register_visualization(media_info['id'])
            
            # Exibir imagem por 30 segundos (ou até tecla ser pressionada)
            start_time = time.time()
            while (time.time() - start_time) < self.IMAGE_DISPLAY_DURATION:
                cv2.imshow(window_name, image)
                
                # Verificar teclas a cada 100ms
                key = cv2.waitKey(100) & 0xFF
                if key == ord("q"):  # Sair
                    return False
                elif key == ord("s"):  # Pular
                    return True
            
            return True
            
        except Exception as e:
            print(f"[ERRO] Não foi possível exibir imagem {image_path}: {e}")
            return True
    
    def play_videos(self):
        """Reproduz as mídias (vídeos e imagens) em loop fullscreen"""
        if not self.current_media:
            print("[INFO] Nenhuma mídia para reproduzir. Aguardando...")
            time.sleep(10)
            return True

        print(
            f"\n[{datetime.now().strftime('%H:%M:%S')}] Reproduzindo {len(self.current_media)} mídia(s) em loop..."
        )
        print("[INFO] Pressione 'q' para sair ou 's' para pular")

        window_name = "Propaganda"
        cv2.namedWindow(window_name, cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty(
            window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN
        )

        while True:
            for i, media_path in enumerate(self.current_media):
                # Encontrar informações da mídia
                media_info = self.downloaded_media[i]
                
                if media_info["is_image"]:
                    # Exibir imagem por 30 segundos
                    continue_playing = self.display_image(media_path, media_info, window_name)
                    if not continue_playing:
                        cv2.destroyAllWindows()
                        return False
                else:
                    # Reproduzir vídeo
                    cap = cv2.VideoCapture(media_path)

                    if not cap.isOpened():
                        print(f"[ERRO] Não foi possível abrir: {media_path}")
                        continue

                    fps = cap.get(cv2.CAP_PROP_FPS)
                    if fps == 0:
                        fps = 30
                    delay = int(1000 / fps)
                    
                    print(f"  ▶️ Reproduzindo vídeo: {media_info['filename']}")
                    
                    # Registrar impressão no primeiro frame
                    impression_registered = False

                    while cap.isOpened():
                        ret, frame = cap.read()

                        if not ret:
                            break
                        
                        # Registrar impressão apenas uma vez
                        if not impression_registered:
                            self.register_visualization(media_info['id'])
                            impression_registered = True

                        cv2.imshow(window_name, frame)

                        key = cv2.waitKey(delay) & 0xFF
                        if key == ord("q"):  # Sair
                            cap.release()
                            cv2.destroyAllWindows()
                            return False
                        elif key == ord("s"):  # Pular
                            break

                    cap.release()

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
        print(f"Duração de imagens: {self.IMAGE_DISPLAY_DURATION} segundos")
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
                    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Verificando atualizações...")
                    check_result = self.check_for_updates()

                    if check_result:
                        has_update, new_timestamp = check_result
                        if has_update and new_timestamp:
                            self.save_last_timestamp(new_timestamp)
                            self.update_videos()

                    last_check = current_time

                # Reproduzir mídias (vídeos e imagens)
                continue_playing = self.play_videos()
                if not continue_playing:
                    break

        except KeyboardInterrupt:
            print("\n\n[INFO] Encerrando cliente...")
        finally:
            cv2.destroyAllWindows()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = input("Digite a URL do servidor (ou deixe vazio para padrão): ").strip()
    while True:
        try:
            client = PropagandaClient(url=url)
            client.run()
        except Exception as e:
            print(f"[ERRO] Ocorreu um erro: {e}")

        time.sleep(5)
