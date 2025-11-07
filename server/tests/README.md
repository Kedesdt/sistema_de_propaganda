# 🧪 Testes do Sistema de Propaganda

## 📋 Visão Geral

Suite completa de testes para o sistema de propaganda com geolocalização.

## 🏗️ Estrutura de Testes

```
tests/
├── __init__.py
├── conftest.py              # Fixtures e configuração
├── test_validators.py       # Testes de validators customizados
├── test_services.py         # Testes de services (lógica de negócio)
└── test_routes.py          # Testes de integração (rotas)
```

## 🚀 Executando os Testes

### Instalar Dependências

```bash
pip install pytest pytest-flask pytest-cov
```

### Rodar Todos os Testes

```bash
cd server
pytest
```

### Rodar com Cobertura

```bash
pytest --cov=. --cov-report=html
```

Relatório será gerado em `htmlcov/index.html`

### Rodar Testes Específicos

```bash
# Apenas validators
pytest tests/test_validators.py

# Apenas services
pytest tests/test_services.py

# Apenas rotas
pytest tests/test_routes.py

# Teste específico
pytest tests/test_validators.py::test_validate_cpf_valido
```

### Rodar com Verbose

```bash
pytest -v
```

### Rodar Testes por Marker

```bash
# Apenas unit tests
pytest -m unit

# Apenas integration tests
pytest -m integration
```

## 📊 Cobertura de Testes

### Validators (100%)
- ✅ CPF/CNPJ validation
- ✅ Telefone BR validation
- ✅ Latitude/Longitude validation
- ✅ Positive number validation

### Services (90%+)
- ✅ VideoService: upload, aprovação, créditos, visualização
- ✅ ClienteService: registro, autenticação, estatísticas
- ✅ AuthService: senha admin, hash

### Routes (85%+)
- ✅ Admin: login, dashboard, gestão de vídeos
- ✅ Cliente: cadastro, login, upload, estatísticas
- ✅ API: timestamp, listagem, download, visualização
- ✅ Error handlers: 404, 500, 403, 413, 429

## 🔧 Fixtures Disponíveis

### `app`
Instância do Flask app configurada para testes com banco em memória

### `client`
Cliente de teste para fazer requisições HTTP

### `authenticated_admin_client`
Cliente autenticado como admin

### `authenticated_cliente_client`
Cliente autenticado como cliente

### `sample_video`
Vídeo de exemplo no banco de dados

### `sample_cliente`
Cliente de exemplo no banco de dados

## 📝 Exemplo de Uso

```python
def test_my_feature(client, sample_video):
    """Testa uma funcionalidade"""
    response = client.get(f'/api/videos?latitude=0&longitude=0')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'videos' in data
```

## 🎯 Boas Práticas

1. **Nomenclatura**: Use `test_` como prefixo
2. **Isolamento**: Cada teste deve ser independente
3. **Clareza**: Use docstrings descritivas
4. **Cobertura**: Teste casos de sucesso E falha
5. **Fixtures**: Reutilize fixtures sempre que possível

## 🐛 Debugging

```bash
# Rodar com debug info
pytest -vv -s

# Parar no primeiro erro
pytest -x

# Mostrar locals em falhas
pytest -l
```

## 📈 CI/CD

Para integração contínua, adicione ao workflow:

```yaml
- name: Run tests
  run: |
    pip install -r requirements.txt
    pytest --cov=. --cov-report=xml
```

## 🔍 Verificar Qualidade

```bash
# Rodar testes + cobertura + relatório
pytest --cov=. --cov-report=term-missing --cov-report=html
```

## ⚠️ Troubleshooting

### "ModuleNotFoundError"
```bash
# Certifique-se de estar no diretório correto
cd server
pytest
```

### "Database locked"
- Testes usam banco em memória (SQLite)
- Não deveria ocorrer lock issues

### "Import errors"
```bash
# Instale todas as dependências
pip install -r requirements.txt
```

## 📚 Documentação Adicional

- [Pytest Documentation](https://docs.pytest.org/)
- [Flask Testing](https://flask.palletsprojects.com/en/latest/testing/)
- [Coverage.py](https://coverage.readthedocs.io/)
