# Módulo de Rotas

Estrutura modular de rotas organizadas por funcionalidade.

## 📂 Estrutura

```
routes/
├── __init__.py      # Exporta todos os blueprints
├── main.py          # Rotas principais (/, /client)
├── api.py           # API REST (/api/*)
├── admin.py         # Área administrativa (/admin/*)
└── cliente.py       # Portal do cliente (/cliente/*)
```

## 📦 Blueprints

### `main_bp` - Rotas Principais

- `GET /` - API info e documentação
- `GET /client` - Interface web do visualizador

### `api_bp` - API REST

- `GET /api/timestamp` - Timestamp da última atualização
- `GET /api/videos` - Lista vídeos por geolocalização
- `GET /api/download/<id>` - Download de vídeo
- `POST /api/visualizacao/<id>` - Registra view e consome crédito

### `admin_bp` - Área Administrativa

- `GET/POST /admin/login` - Login do admin
- `GET /admin/logout` - Logout
- `GET /admin/` - Dashboard
- `POST /admin/upload` - Upload de vídeo
- `POST /admin/aprovar/<id>` - Aprovar vídeo
- `POST /admin/reprovar/<id>` - Reprovar vídeo
- `POST /admin/marcar-pago/<id>` - Marcar como pago
- `POST /admin/adicionar-creditos/<id>` - Adicionar créditos
- `POST /admin/pausar/<id>` - Pausar/despausar vídeo
- `POST /admin/delete/<id>` - Deletar vídeo
- `GET /admin/download-client` - Download do client.exe

### `cliente_bp` - Portal do Cliente

- `GET/POST /cliente/login` - Login do cliente
- `GET/POST /cliente/register` - Registro de novo cliente
- `GET /cliente/logout` - Logout
- `GET /cliente/dashboard` - Dashboard do cliente
- `POST /cliente/upload` - Upload de vídeo
- `GET /cliente/video/<id>/stats` - Estatísticas do vídeo

## 🔧 Como Usar

### Importar blueprints no app.py:

```python
from routes import main_bp, api_bp, admin_bp, cliente_bp

app.register_blueprint(main_bp)
app.register_blueprint(api_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(cliente_bp)
```

### Adicionar novas rotas:

1. Escolha o arquivo apropriado (main.py, api.py, admin.py, cliente.py)
2. Adicione a rota usando o decorator do blueprint:

```python
@admin_bp.route('/nova-rota')
def nova_funcao():
    return "Olá"
```

3. Não é necessário registrar novamente no app.py

## 📝 Padrões

- **Autenticação Admin**: `session.get('admin_logged_in')`
- **Autenticação Cliente**: `session.get('cliente_id')`
- **Flash messages**: `flash(mensagem, categoria)`
- **Redirecionamento**: `redirect(url_for('blueprint.funcao'))`
- **Query params**: `request.args.get('param')`
- **Form data**: `request.form.get('campo')`
- **JSON data**: `request.get_json()`

## 🔐 Segurança

Todas as rotas administrativas e do cliente verificam autenticação antes de executar.

Rotas protegidas retornam:

- Admin: Redirect para `/admin/login`
- Cliente: Redirect para `/cliente/login`
- API: HTTP 401/403
