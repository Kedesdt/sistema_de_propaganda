"""
Configuração de fixtures para testes
"""
import pytest
import os
import sys
from flask import Flask

# Adicionar diretório pai ao path para importar módulos
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from models import db, Video, Cliente, SystemStatus
from config import Config


class TestConfig(Config):
    """Configuração para testes"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # Banco em memória
    WTF_CSRF_ENABLED = False  # Desabilitar CSRF para testes
    UPLOAD_FOLDER = 'test_uploads'
    SECRET_KEY = 'test-secret-key'
    ADMIN_PASSWORD = 'admin123'


@pytest.fixture
def app():
    """Cria e configura uma instância do app para testes"""
    app = create_app()
    app.config.from_object(TestConfig)
    
    with app.app_context():
        db.create_all()
        
        # Inicializar SystemStatus
        status = SystemStatus()
        db.session.add(status)
        db.session.commit()
        
        yield app
        
        # Cleanup
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Cliente de teste para fazer requisições"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Runner para comandos CLI"""
    return app.test_cli_runner()


@pytest.fixture
def authenticated_admin_client(client):
    """Cliente autenticado como admin"""
    with client.session_transaction() as session:
        session['admin_logged_in'] = True
    return client


@pytest.fixture
def sample_video(app):
    """Cria um vídeo de exemplo no banco"""
    with app.app_context():
        video = Video(
            filename='test_video.mp4',
            original_filename='test_video.mp4',
            latitude=-23.5505,
            longitude=-46.6333,
            radius_km=10.0,
            aprovado=True,
            pago=True,
            creditos=100,
            pausado=False
        )
        db.session.add(video)
        db.session.commit()
        return video


@pytest.fixture
def sample_cliente(app):
    """Cria um cliente de exemplo no banco"""
    with app.app_context():
        cliente = Cliente(
            nome='João Silva',
            email='joao@example.com',
            cpf_cnpj='12345678901',
            telefone='11987654321',
            endereco='Rua Teste, 123'
        )
        cliente.set_password('senha123')
        db.session.add(cliente)
        db.session.commit()
        return cliente


@pytest.fixture
def authenticated_cliente_client(client, sample_cliente):
    """Cliente autenticado como cliente"""
    with client.session_transaction() as session:
        session['cliente_id'] = sample_cliente.id
        session['cliente_nome'] = sample_cliente.nome
    return client
