"""
Serviço para gerenciamento de vídeos
"""

import os
from werkzeug.utils import secure_filename
from models import db, Video, LogVisualizacao
from flask import current_app
from datetime import datetime


class VideoService:
    """Serviço para operações com vídeos"""

    @staticmethod
    def upload_video(file, latitude, longitude, radius_km, cliente_id=None):
        """
        Upload de vídeo com validação e salvamento

        Args:
            file: FileStorage object do Flask
            latitude: float
            longitude: float
            radius_km: float
            cliente_id: int (opcional, para vídeos de cliente)

        Returns:
            tuple: (Video, error_message)
        """
        try:
            # Validar arquivo
            if not file or file.filename == "":
                return None, "Nenhum arquivo selecionado"

            # Validar extensão
            allowed_extensions = {".mp4", ".avi", ".mov", ".mkv"}
            ext = os.path.splitext(file.filename)[1].lower()
            if ext not in allowed_extensions:
                return (
                    None,
                    f'Tipo de arquivo não permitido. Use: {", ".join(allowed_extensions)}',
                )

            # Validar coordenadas
            if not (-90 <= latitude <= 90):
                return None, "Latitude inválida (-90 a 90)"
            if not (-180 <= longitude <= 180):
                return None, "Longitude inválida (-180 a 180)"
            if radius_km <= 0:
                return None, "Raio deve ser maior que zero"

            # Salvar arquivo
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{filename}"

            upload_folder = current_app.config["UPLOAD_FOLDER"]
            os.makedirs(upload_folder, exist_ok=True)
            filepath = os.path.join(upload_folder, filename)
            file.save(filepath)

            # Criar registro no banco
            video = Video(
                filename=filename,
                original_filename=file.filename,
                latitude=latitude,
                longitude=longitude,
                radius_km=radius_km,
                cliente_id=cliente_id,
                aprovado=(cliente_id is None),  # Admin aprova automaticamente
                pago=(cliente_id is None),
                creditos=(
                    0 if cliente_id else 1000
                ),  # Admin tem créditos ilimitados inicialmente
            )

            db.session.add(video)
            db.session.commit()

            current_app.logger.info(
                f"Vídeo {filename} enviado com sucesso (Cliente: {cliente_id})"
            )
            return video, None

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Erro ao fazer upload: {str(e)}")
            return None, f"Erro ao fazer upload: {str(e)}"

    @staticmethod
    def aprovar_video(video_id):
        """Aprovar vídeo de cliente"""
        try:
            video = Video.query.get_or_404(video_id)
            video.aprovado = True
            db.session.commit()
            current_app.logger.info(f"Vídeo {video.filename} aprovado")
            return True, "Vídeo aprovado com sucesso"
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Erro ao aprovar vídeo {video_id}: {str(e)}")
            return False, f"Erro ao aprovar vídeo: {str(e)}"

    @staticmethod
    def reprovar_video(video_id):
        """Reprovar vídeo de cliente"""
        try:
            video = Video.query.get_or_404(video_id)
            video.aprovado = False
            db.session.commit()
            current_app.logger.info(f"Vídeo {video.filename} reprovado")
            return True, "Vídeo reprovado"
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Erro ao reprovar vídeo {video_id}: {str(e)}")
            return False, f"Erro ao reprovar vídeo: {str(e)}"

    @staticmethod
    def marcar_como_pago(video_id):
        """Marcar vídeo como pago"""
        try:
            video = Video.query.get_or_404(video_id)
            video.pago = True
            db.session.commit()
            current_app.logger.info(f"Vídeo {video.filename} marcado como pago")
            return True, "Vídeo marcado como pago"
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(
                f"Erro ao marcar vídeo {video_id} como pago: {str(e)}"
            )
            return False, f"Erro ao marcar como pago: {str(e)}"

    @staticmethod
    def adicionar_creditos(video_id, quantidade):
        """Adicionar créditos a um vídeo"""
        try:
            if quantidade <= 0:
                return False, "Quantidade deve ser maior que zero"

            video = Video.query.get_or_404(video_id)
            video.creditos += quantidade
            video.pausado = False  # Despausar ao adicionar créditos
            db.session.commit()

            current_app.logger.info(
                f"{quantidade} créditos adicionados ao vídeo {video.filename}"
            )
            return True, f"{quantidade} créditos adicionados com sucesso"
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(
                f"Erro ao adicionar créditos ao vídeo {video_id}: {str(e)}"
            )
            return False, f"Erro ao adicionar créditos: {str(e)}"

    @staticmethod
    def pausar_video(video_id):
        """Pausar/despausar vídeo"""
        try:
            video = Video.query.get_or_404(video_id)
            video.pausado = not video.pausado
            db.session.commit()

            status = "pausado" if video.pausado else "despausado"
            current_app.logger.info(f"Vídeo {video.filename} {status}")
            return True, f"Vídeo {status} com sucesso"
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Erro ao pausar vídeo {video_id}: {str(e)}")
            return False, f"Erro ao pausar vídeo: {str(e)}"

    @staticmethod
    def registrar_visualizacao(video_id, ip_address, latitude=None, longitude=None):
        """
        Registra uma visualização e consome 1 crédito

        Returns:
            tuple: (success, message, video)
        """
        try:
            video = Video.query.get_or_404(video_id)

            # Verificar se está aprovado
            if not video.aprovado:
                return False, "Vídeo não aprovado", video

            # Verificar se tem créditos
            if video.creditos <= 0:
                video.pausado = True
                db.session.commit()
                return False, "Vídeo sem créditos", video

            # Verificar se está pausado
            if video.pausado:
                return False, "Vídeo pausado", video

            # Registrar visualização
            log = LogVisualizacao(
                video_id=video_id,
                ip_address=ip_address,
                latitude=latitude,
                longitude=longitude,
            )
            db.session.add(log)

            # Consumir crédito
            video.creditos -= 1
            video.visualizacoes += 1

            # Pausar se acabaram os créditos
            if video.creditos <= 0:
                video.pausado = True

            db.session.commit()

            current_app.logger.info(
                f"Visualização registrada: {video.filename} (Créditos restantes: {video.creditos})"
            )
            return True, "Visualização registrada", video

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(
                f"Erro ao registrar visualização do vídeo {video_id}: {str(e)}"
            )
            return False, f"Erro ao registrar visualização: {str(e)}", None

    @staticmethod
    def deletar_video(video_id):
        """Deletar vídeo e arquivo físico"""
        try:
            video = Video.query.get_or_404(video_id)
            filename = video.filename

            # Deletar arquivo físico
            filepath = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
            if os.path.exists(filepath):
                os.remove(filepath)

            # Deletar do banco
            db.session.delete(video)
            db.session.commit()

            current_app.logger.info(f"Vídeo {filename} deletado")
            return True, "Vídeo deletado com sucesso"
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Erro ao deletar vídeo {video_id}: {str(e)}")
            return False, f"Erro ao deletar vídeo: {str(e)}"

    @staticmethod
    def get_videos_by_location(latitude, longitude):
        """
        Retorna vídeos aprovados e ativos para uma localização

        Args:
            latitude: float
            longitude: float

        Returns:
            list: Lista de vídeos ordenados por prioridade
        """
        from utils.geo import is_within_radius

        videos = (
            Video.query.filter_by(aprovado=True, pausado=False)
            .filter(Video.creditos > 0)
            .all()
        )

        # Filtrar por geolocalização
        videos_filtrados = [
            video
            for video in videos
            if is_within_radius(
                latitude, longitude, video.latitude, video.longitude, video.radius_km
            )
        ]

        # Ordenar por créditos (prioridade)
        videos_filtrados.sort(key=lambda v: v.creditos, reverse=True)

        return videos_filtrados

    @staticmethod
    def get_all_videos():
        """Retorna todos os vídeos ordenados por ID decrescente"""
        return Video.query.order_by(Video.id.desc()).all()

    @staticmethod
    def get_videos_pendentes():
        """Retorna vídeos pendentes de aprovação"""
        return Video.query.filter_by(aprovado=False).order_by(Video.id.desc()).all()

    @staticmethod
    def get_videos_nao_pagos():
        """Retorna vídeos não pagos"""
        return Video.query.filter_by(pago=False).order_by(Video.id.desc()).all()
