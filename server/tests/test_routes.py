"""
Testes de integração para as rotas
"""
import pytest
import json
from models import db, Video


class TestAdminRoutes:
    """Testes para rotas administrativas"""
    
    def test_login_page(self, client):
        """Testa acesso à página de login"""
        response = client.get('/admin/login')
        assert response.status_code == 200
    
    def test_login_sucesso(self, client):
        """Testa login com sucesso"""
        response = client.post('/admin/login', data={
            'password': 'admin123',
            'submit': True
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Dashboard' in response.data or b'dashboard' in response.data
    
    def test_login_falha(self, client):
        """Testa login com senha errada"""
        response = client.post('/admin/login', data={
            'password': 'senha_errada',
            'submit': True
        })
        
        assert b'incorreta' in response.data or b'Senha incorreta' in response.data
    
    def test_dashboard_sem_autenticacao(self, client):
        """Testa acesso ao dashboard sem autenticação"""
        response = client.get('/admin/', follow_redirects=False)
        assert response.status_code == 302  # Redirect para login
    
    def test_dashboard_com_autenticacao(self, authenticated_admin_client):
        """Testa acesso ao dashboard com autenticação"""
        response = authenticated_admin_client.get('/admin/')
        assert response.status_code == 200
    
    def test_logout(self, authenticated_admin_client):
        """Testa logout"""
        response = authenticated_admin_client.get('/admin/logout', follow_redirects=True)
        assert response.status_code == 200
    
    def test_aprovar_video(self, authenticated_admin_client, sample_video, app):
        """Testa aprovação de vídeo"""
        with app.app_context():
            sample_video.aprovado = False
            db.session.commit()
        
        response = authenticated_admin_client.post(
            f'/admin/aprovar/{sample_video.id}',
            follow_redirects=True
        )
        assert response.status_code == 200
    
    def test_reprovar_video(self, authenticated_admin_client, sample_video):
        """Testa reprovação de vídeo"""
        response = authenticated_admin_client.post(
            f'/admin/reprovar/{sample_video.id}',
            follow_redirects=True
        )
        assert response.status_code == 200
    
    def test_adicionar_creditos(self, authenticated_admin_client, sample_video):
        """Testa adição de créditos"""
        response = authenticated_admin_client.post(
            f'/admin/adicionar-creditos/{sample_video.id}',
            data={'creditos': '50'},
            follow_redirects=True
        )
        assert response.status_code == 200
    
    def test_pausar_video(self, authenticated_admin_client, sample_video):
        """Testa pausar vídeo"""
        response = authenticated_admin_client.post(
            f'/admin/pausar/{sample_video.id}',
            follow_redirects=True
        )
        assert response.status_code == 200


class TestClienteRoutes:
    """Testes para rotas do cliente"""
    
    def test_login_page(self, client):
        """Testa acesso à página de login"""
        response = client.get('/cliente/login')
        assert response.status_code == 200
    
    def test_register_page(self, client):
        """Testa acesso à página de cadastro"""
        response = client.get('/cliente/register')
        assert response.status_code == 200
    
    def test_register_sucesso(self, client):
        """Testa cadastro de novo cliente"""
        response = client.post('/cliente/register', data={
            'nome': 'Teste Cliente',
            'email': 'teste@example.com',
            'senha': 'senha123',
            'confirmar_senha': 'senha123',
            'cpf_cnpj': '11144477735',
            'telefone': '11987654321',
            'endereco': 'Rua Teste, 123',
            'submit': True
        }, follow_redirects=True)
        
        assert response.status_code == 200
    
    def test_login_sucesso(self, client, sample_cliente):
        """Testa login de cliente com sucesso"""
        response = client.post('/cliente/login', data={
            'email': sample_cliente.email,
            'senha': 'senha123',
            'submit': True
        }, follow_redirects=True)
        
        assert response.status_code == 200
    
    def test_login_falha(self, client, sample_cliente):
        """Testa login com senha errada"""
        response = client.post('/cliente/login', data={
            'email': sample_cliente.email,
            'senha': 'senha_errada',
            'submit': True
        })
        
        assert b'incorretos' in response.data or b'Email ou senha incorretos' in response.data
    
    def test_dashboard_sem_autenticacao(self, client):
        """Testa acesso ao dashboard sem autenticação"""
        response = client.get('/cliente/dashboard', follow_redirects=False)
        assert response.status_code == 302  # Redirect para login
    
    def test_dashboard_com_autenticacao(self, authenticated_cliente_client):
        """Testa acesso ao dashboard com autenticação"""
        response = authenticated_cliente_client.get('/cliente/dashboard')
        assert response.status_code == 200
    
    def test_logout(self, authenticated_cliente_client):
        """Testa logout"""
        response = authenticated_cliente_client.get('/cliente/logout', follow_redirects=True)
        assert response.status_code == 200


class TestAPIRoutes:
    """Testes para rotas da API"""
    
    def test_get_timestamp(self, client):
        """Testa endpoint de timestamp"""
        response = client.get('/api/timestamp')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'last_update' in data
        assert 'timestamp' in data
    
    def test_get_videos_sem_parametros(self, client):
        """Testa busca de vídeos sem parâmetros"""
        response = client.get('/api/videos')
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_get_videos_com_parametros(self, client, sample_video):
        """Testa busca de vídeos com parâmetros válidos"""
        response = client.get('/api/videos?latitude=-23.5505&longitude=-46.6333')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'videos' in data
        assert 'count' in data
        assert isinstance(data['videos'], list)
    
    def test_registrar_visualizacao(self, client, sample_video):
        """Testa registro de visualização"""
        response = client.post(
            f'/api/visualizacao/{sample_video.id}',
            data=json.dumps({'latitude': -23.5505, 'longitude': -46.6333}),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        assert 'creditos_restantes' in data
    
    def test_registrar_visualizacao_video_pausado(self, client, sample_video, app):
        """Testa registro de visualização em vídeo pausado"""
        with app.app_context():
            sample_video.pausado = True
            db.session.commit()
        
        response = client.post(
            f'/api/visualizacao/{sample_video.id}',
            data=json.dumps({}),
            content_type='application/json'
        )
        
        assert response.status_code in [402, 403]
        data = json.loads(response.data)
        assert 'error' in data


class TestErrorHandlers:
    """Testes para error handlers"""
    
    def test_404_page(self, client):
        """Testa página 404"""
        response = client.get('/pagina-inexistente')
        assert response.status_code == 404
    
    def test_404_api(self, client):
        """Testa 404 em rota de API"""
        response = client.get('/api/rota-inexistente')
        assert response.status_code == 404
        
        data = json.loads(response.data)
        assert 'error' in data
