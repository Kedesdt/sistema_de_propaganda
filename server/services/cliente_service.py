"""
Serviço para gerenciamento de clientes
"""

from models import db, Cliente, Video, LogVisualizacao
from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash


class ClienteService:
    """Serviço para operações com clientes"""

    @staticmethod
    def registrar_cliente(nome, email, senha, cpf_cnpj, telefone, endereco):
        """
        Registra um novo cliente

        Returns:
            tuple: (Cliente, error_message)
        """
        try:
            # Verificar se email já existe
            if Cliente.query.filter_by(email=email).first():
                return None, "Email já cadastrado"

            # Verificar se CPF/CNPJ já existe
            if Cliente.query.filter_by(cpf_cnpj=cpf_cnpj).first():
                return None, "CPF/CNPJ já cadastrado"

            # Criar cliente
            cliente = Cliente(
                nome=nome,
                email=email,
                cpf_cnpj=cpf_cnpj,
                telefone=telefone,
                endereco=endereco,
            )
            cliente.set_password(senha)

            db.session.add(cliente)
            db.session.commit()

            current_app.logger.info(f"Novo cliente registrado: {email}")
            return cliente, None

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Erro ao registrar cliente: {str(e)}")
            return None, f"Erro ao registrar: {str(e)}"

    @staticmethod
    def autenticar_cliente(email, senha):
        """
        Autentica um cliente

        Returns:
            Cliente or None
        """
        cliente = Cliente.query.filter_by(email=email).first()

        if cliente and cliente.check_password(senha):
            current_app.logger.info(f"Cliente autenticado: {email}")
            return cliente

        current_app.logger.warning(f"Tentativa de login falhou: {email}")
        return None

    @staticmethod
    def get_cliente_by_id(cliente_id):
        """Retorna cliente por ID"""
        return Cliente.query.get(cliente_id)

    @staticmethod
    def get_videos_cliente(cliente_id):
        """Retorna todos os vídeos de um cliente"""
        return (
            Video.query.filter_by(cliente_id=cliente_id).order_by(Video.id.desc()).all()
        )

    @staticmethod
    def get_estatisticas_video(video_id, cliente_id):
        """
        Retorna estatísticas de um vídeo

        Returns:
            dict or None
        """
        video = Video.query.filter_by(id=video_id, cliente_id=cliente_id).first()

        if not video:
            return None

        visualizacoes = (
            LogVisualizacao.query.filter_by(video_id=video_id)
            .order_by(LogVisualizacao.timestamp.desc())
            .limit(100)
            .all()
        )

        return {
            "video": video,
            "visualizacoes": visualizacoes,
            "total_visualizacoes": video.visualizacoes,
            "creditos_restantes": video.creditos,
            "status": (
                "Ativo" if not video.pausado and video.creditos > 0 else "Pausado"
            ),
        }

    @staticmethod
    def get_dashboard_stats(cliente_id):
        """Retorna estatísticas do dashboard do cliente"""
        videos = Video.query.filter_by(cliente_id=cliente_id).all()

        total_videos = len(videos)
        videos_aprovados = sum(1 for v in videos if v.aprovado)
        videos_pendentes = sum(1 for v in videos if not v.aprovado)
        total_visualizacoes = sum(v.visualizacoes for v in videos)
        creditos_totais = sum(v.creditos for v in videos)

        return {
            "total_videos": total_videos,
            "videos_aprovados": videos_aprovados,
            "videos_pendentes": videos_pendentes,
            "total_visualizacoes": total_visualizacoes,
            "creditos_totais": creditos_totais,
            "videos": videos,
        }
