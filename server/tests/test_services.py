"""
Testes para os services
"""
import pytest
from services import VideoService, ClienteService, AuthService
from models import db, Video, Cliente


class TestVideoService:
    """Testes para VideoService"""
    
    def test_get_all_videos(self, app):
        """Testa buscar todos os vídeos"""
        with app.app_context():
            # Criar alguns vídeos
            video1 = Video(filename='v1.mp4', latitude=0, longitude=0, radius_km=10)
            video2 = Video(filename='v2.mp4', latitude=0, longitude=0, radius_km=10)
            db.session.add_all([video1, video2])
            db.session.commit()
            
            videos = VideoService.get_all_videos()
            assert len(videos) == 2
    
    def test_aprovar_video(self, app, sample_video):
        """Testa aprovação de vídeo"""
        with app.app_context():
            sample_video.aprovado = False
            db.session.commit()
            
            success, message = VideoService.aprovar_video(sample_video.id)
            assert success == True
            assert 'aprovado' in message.lower()
            
            video = Video.query.get(sample_video.id)
            assert video.aprovado == True
    
    def test_reprovar_video(self, app, sample_video):
        """Testa reprovação de vídeo"""
        with app.app_context():
            success, message = VideoService.reprovar_video(sample_video.id)
            assert success == True
            
            video = Video.query.get(sample_video.id)
            assert video.aprovado == False
    
    def test_adicionar_creditos(self, app, sample_video):
        """Testa adição de créditos"""
        with app.app_context():
            creditos_iniciais = sample_video.creditos
            quantidade = 50
            
            success, message = VideoService.adicionar_creditos(sample_video.id, quantidade)
            assert success == True
            
            video = Video.query.get(sample_video.id)
            assert video.creditos == creditos_iniciais + quantidade
            assert video.pausado == False  # Deve despausar
    
    def test_adicionar_creditos_quantidade_invalida(self, app, sample_video):
        """Testa adição de créditos com quantidade inválida"""
        with app.app_context():
            success, message = VideoService.adicionar_creditos(sample_video.id, 0)
            assert success == False
            assert 'maior que zero' in message.lower()
    
    def test_pausar_video(self, app, sample_video):
        """Testa pausar/despausar vídeo"""
        with app.app_context():
            pausado_inicial = sample_video.pausado
            
            success, message = VideoService.pausar_video(sample_video.id)
            assert success == True
            
            video = Video.query.get(sample_video.id)
            assert video.pausado != pausado_inicial
    
    def test_registrar_visualizacao(self, app, sample_video):
        """Testa registro de visualização"""
        with app.app_context():
            creditos_iniciais = sample_video.creditos
            
            success, message, video = VideoService.registrar_visualizacao(
                sample_video.id,
                '127.0.0.1',
                -23.5505,
                -46.6333
            )
            
            assert success == True
            assert video.creditos == creditos_iniciais - 1
            assert video.visualizacoes == 1
    
    def test_registrar_visualizacao_video_pausado(self, app, sample_video):
        """Testa registro de visualização em vídeo pausado"""
        with app.app_context():
            sample_video.pausado = True
            db.session.commit()
            
            success, message, video = VideoService.registrar_visualizacao(
                sample_video.id,
                '127.0.0.1'
            )
            
            assert success == False
            assert 'pausado' in message.lower()
    
    def test_registrar_visualizacao_sem_creditos(self, app, sample_video):
        """Testa registro de visualização sem créditos"""
        with app.app_context():
            sample_video.creditos = 0
            db.session.commit()
            
            success, message, video = VideoService.registrar_visualizacao(
                sample_video.id,
                '127.0.0.1'
            )
            
            assert success == False
            assert 'crédito' in message.lower()
    
    def test_get_videos_by_location(self, app):
        """Testa busca de vídeos por localização"""
        with app.app_context():
            # Criar vídeo em São Paulo
            video = Video(
                filename='sp.mp4',
                latitude=-23.5505,
                longitude=-46.6333,
                radius_km=50,
                aprovado=True,
                pago=True,
                pausado=False,
                creditos=10
            )
            db.session.add(video)
            db.session.commit()
            
            # Buscar próximo a São Paulo (dentro do raio)
            videos = VideoService.get_videos_by_location(-23.5600, -46.6400)
            assert len(videos) >= 1
            
            # Buscar longe de São Paulo (fora do raio)
            videos = VideoService.get_videos_by_location(0, 0)
            assert len(videos) == 0


class TestClienteService:
    """Testes para ClienteService"""
    
    def test_registrar_cliente(self, app):
        """Testa registro de novo cliente"""
        with app.app_context():
            cliente, error = ClienteService.registrar_cliente(
                nome='Maria Santos',
                email='maria@example.com',
                senha='senha123',
                cpf_cnpj='12345678901',
                telefone='11987654321',
                endereco='Rua Teste, 456'
            )
            
            assert cliente is not None
            assert error is None
            assert cliente.nome == 'Maria Santos'
            assert cliente.email == 'maria@example.com'
    
    def test_registrar_cliente_email_duplicado(self, app, sample_cliente):
        """Testa registro com email duplicado"""
        with app.app_context():
            cliente, error = ClienteService.registrar_cliente(
                nome='Outro Nome',
                email=sample_cliente.email,
                senha='senha123',
                cpf_cnpj='98765432109',
                telefone='11987654321',
                endereco='Rua Teste, 456'
            )
            
            assert cliente is None
            assert error is not None
            assert 'email' in error.lower()
    
    def test_registrar_cliente_cpf_duplicado(self, app, sample_cliente):
        """Testa registro com CPF duplicado"""
        with app.app_context():
            cliente, error = ClienteService.registrar_cliente(
                nome='Outro Nome',
                email='outro@example.com',
                senha='senha123',
                cpf_cnpj=sample_cliente.cpf_cnpj,
                telefone='11987654321',
                endereco='Rua Teste, 456'
            )
            
            assert cliente is None
            assert error is not None
            assert 'cpf' in error.lower() or 'cnpj' in error.lower()
    
    def test_autenticar_cliente_sucesso(self, app, sample_cliente):
        """Testa autenticação de cliente com sucesso"""
        with app.app_context():
            cliente = ClienteService.autenticar_cliente(
                sample_cliente.email,
                'senha123'
            )
            
            assert cliente is not None
            assert cliente.id == sample_cliente.id
    
    def test_autenticar_cliente_senha_errada(self, app, sample_cliente):
        """Testa autenticação com senha errada"""
        with app.app_context():
            cliente = ClienteService.autenticar_cliente(
                sample_cliente.email,
                'senha_errada'
            )
            
            assert cliente is None
    
    def test_autenticar_cliente_email_inexistente(self, app):
        """Testa autenticação com email inexistente"""
        with app.app_context():
            cliente = ClienteService.autenticar_cliente(
                'inexistente@example.com',
                'senha123'
            )
            
            assert cliente is None
    
    def test_get_cliente_by_id(self, app, sample_cliente):
        """Testa buscar cliente por ID"""
        with app.app_context():
            cliente = ClienteService.get_cliente_by_id(sample_cliente.id)
            assert cliente is not None
            assert cliente.email == sample_cliente.email
    
    def test_get_dashboard_stats(self, app, sample_cliente):
        """Testa estatísticas do dashboard"""
        with app.app_context():
            # Criar alguns vídeos para o cliente
            video1 = Video(
                filename='v1.mp4',
                latitude=0,
                longitude=0,
                radius_km=10,
                cliente_id=sample_cliente.id,
                aprovado=True,
                visualizacoes=10
            )
            video2 = Video(
                filename='v2.mp4',
                latitude=0,
                longitude=0,
                radius_km=10,
                cliente_id=sample_cliente.id,
                aprovado=False,
                visualizacoes=5
            )
            db.session.add_all([video1, video2])
            db.session.commit()
            
            stats = ClienteService.get_dashboard_stats(sample_cliente.id)
            
            assert stats['total_videos'] == 2
            assert stats['videos_aprovados'] == 1
            assert stats['videos_pendentes'] == 1
            assert stats['total_visualizacoes'] == 15


class TestAuthService:
    """Testes para AuthService"""
    
    def test_verificar_senha_admin_correta(self, app):
        """Testa verificação de senha admin correta"""
        with app.app_context():
            result = AuthService.verificar_senha_admin('admin123')
            assert result == True
    
    def test_verificar_senha_admin_incorreta(self, app):
        """Testa verificação de senha admin incorreta"""
        with app.app_context():
            result = AuthService.verificar_senha_admin('senha_errada')
            assert result == False
    
    def test_hash_password(self):
        """Testa geração de hash"""
        hash1 = AuthService.hash_password('senha123')
        hash2 = AuthService.hash_password('senha123')
        
        assert hash1 == hash2  # Mesmo input gera mesmo hash
        assert len(hash1) == 64  # SHA256 gera 64 caracteres hex
    
    def test_verify_password(self):
        """Testa verificação de senha"""
        senha = 'minha_senha'
        hash_senha = AuthService.hash_password(senha)
        
        assert AuthService.verify_password(senha, hash_senha) == True
        assert AuthService.verify_password('outra_senha', hash_senha) == False
