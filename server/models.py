from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Cliente(db.Model):
    __tablename__ = "clientes"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    telefone = db.Column(db.String(50))
    cpf_cnpj = db.Column(db.String(20), unique=True)
    senha = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    endereco = db.Column(db.String(200), nullable=False)

    # Relacionamento com vídeos
    videos = db.relationship("Video", backref="cliente", lazy=True)

    def __repr__(self):
        return f"<Cliente {self.nome}>"

    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "email": self.email,
            "telefone": self.telefone,
            "cpf_cnpj": self.cpf_cnpj,
            "endereco": self.endereco,
            "created_at": self.created_at.isoformat(),
        }

    def set_password(self, senha):
        """Define a senha com hash seguro usando AuthService"""
        from services.auth_service import AuthService

        self.senha = AuthService.hash_password(senha)

    def check_password(self, senha):
        """Verifica se a senha está correta usando AuthService"""
        from services.auth_service import AuthService

        return AuthService.verify_password(senha, self.senha)


class Video(db.Model):
    __tablename__ = "videos"

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    radius_km = db.Column(db.Float, nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Novos campos
    cliente_id = db.Column(db.Integer, db.ForeignKey("clientes.id"), nullable=True)
    aprovado = db.Column(db.Boolean, default=False, nullable=False)
    pago = db.Column(db.Boolean, default=False, nullable=False)
    creditos = db.Column(db.Integer, default=0, nullable=False)
    pausado = db.Column(db.Boolean, default=False, nullable=False)
    visualizacoes = db.Column(db.Integer, default=0, nullable=False)

    # Relacionamento com visualizações
    logs_visualizacao = db.relationship(
        "LogVisualizacao", backref="video", lazy=True, cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Video {self.filename}>"

    def to_dict(self):
        return {
            "id": self.id,
            "filename": self.filename,
            "original_filename": self.original_filename,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "radius_km": self.radius_km,
            "uploaded_at": self.uploaded_at.isoformat(),
            "cliente_id": self.cliente_id,
            "aprovado": self.aprovado,
            "pago": self.pago,
            "creditos": self.creditos,
            "pausado": self.pausado,
            "visualizacoes": self.visualizacoes,
        }

    def consumir_credito(self):
        """Consome 1 crédito e pausa se acabar"""
        if self.creditos > 0:
            self.creditos -= 1
            self.visualizacoes += 1
            if self.creditos == 0:
                self.pausado = True
            return True
        return False

    def adicionar_creditos(self, quantidade):
        """Adiciona créditos e despausa se necessário"""
        self.creditos += quantidade
        if self.creditos > 0:
            self.pausado = False


class LogVisualizacao(db.Model):
    __tablename__ = "logs_visualizacao"

    id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.Integer, db.ForeignKey("videos.id"), nullable=False)
    client_ip = db.Column(db.String(50))
    client_latitude = db.Column(db.Float)
    client_longitude = db.Column(db.Float)
    visualizado_em = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<LogVisualizacao video_id={self.video_id} em {self.visualizado_em}>"


class SystemStatus(db.Model):
    __tablename__ = "system_status"

    id = db.Column(db.Integer, primary_key=True)
    last_update = db.Column(db.DateTime, default=datetime.utcnow)

    @staticmethod
    def get_last_update():
        status = SystemStatus.query.first()
        if not status:
            status = SystemStatus()
            db.session.add(status)
            db.session.commit()
        return status.last_update

    @staticmethod
    def update_timestamp():
        status = SystemStatus.query.first()
        if not status:
            status = SystemStatus()
            db.session.add(status)
        status.last_update = datetime.utcnow()
        db.session.commit()
        return status.last_update
