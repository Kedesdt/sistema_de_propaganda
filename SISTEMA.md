# 📺 Sistema de Propaganda com Geolocalização

## 📖 Visão Geral

Sistema completo de propaganda digital baseado em localização geográfica. O sistema permite que vídeos sejam exibidos automaticamente em clientes localizados em áreas geográficas específicas.

## 🏗️ Arquitetura

O sistema é dividido em duas partes principais:

### 1. **Servidor (Flask)**
- API REST para gerenciamento de vídeos
- Painel administrativo web
- Banco de dados SQLite
- Sistema de geolocalização
- Controle de sincronização por timestamp

### 2. **Cliente (Python)**
- Aplicação standalone (pode ser compilada em .exe)
- Verifica atualizações periodicamente
- Baixa vídeos automaticamente baseado na localização
- Reproduz vídeos em fullscreen

## 🔄 Fluxo de Funcionamento

```
┌─────────────────────────────────────────────────────────────┐
│                         SERVIDOR                             │
│  ┌────────────────────────────────────────────────────┐     │
│  │              Painel Admin                          │     │
│  │  • Login com senha                                 │     │
│  │  • Upload de vídeos                                │     │
│  │  • Definir localização (lat, lon, raio)           │     │
│  │  • Download do client.exe                          │     │
│  └────────────────────────────────────────────────────┘     │
│                           ▼                                  │
│  ┌────────────────────────────────────────────────────┐     │
│  │           Banco de Dados                           │     │
│  │  • Tabela: videos                                  │     │
│  │    - id, filename, latitude, longitude, radius_km  │     │
│  │  • Tabela: system_status                           │     │
│  │    - last_update (timestamp)                       │     │
│  └────────────────────────────────────────────────────┘     │
│                           ▼                                  │
│  ┌────────────────────────────────────────────────────┐     │
│  │                API REST                            │     │
│  │  GET /api/timestamp                                │     │
│  │  GET /api/videos?lat=X&lon=Y                       │     │
│  │  GET /api/download/<video_id>                      │     │
│  └────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────┘
                           ▲
                           │ HTTP Requests
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                        CLIENTE                               │
│  ┌────────────────────────────────────────────────────┐     │
│  │            Loop Infinito (5 min)                   │     │
│  │  1. Verificar timestamp do servidor                │     │
│  │  2. Se houver atualização:                         │     │
│  │     • Buscar vídeos para minha localização         │     │
│  │     • Baixar vídeos novos                          │     │
│  │  3. Reproduzir vídeos em fullscreen (loop)         │     │
│  └────────────────────────────────────────────────────┘     │
│                                                              │
│  Configuração:                                               │
│  • CLIENT_LATITUDE: -23.5505                                 │
│  • CLIENT_LONGITUDE: -46.6333                                │
│  • CHECK_INTERVAL: 300 segundos                              │
└─────────────────────────────────────────────────────────────┘
```

## 🗺️ Sistema de Geolocalização

### Como Funciona

Cada vídeo cadastrado possui:
- **Latitude**: Coordenada do ponto central (-90 a 90)
- **Longitude**: Coordenada do ponto central (-180 a 180)
- **Raio (km)**: Distância em quilômetros a partir do ponto central

### Exemplo Prático

```python
# Vídeo cadastrado no servidor:
Video 1:
  - Localização: Shopping Ibirapuera, São Paulo
  - Latitude: -23.5505
  - Longitude: -46.6333
  - Raio: 5 km

# Cliente rodando em:
  - Latitude: -23.5600
  - Longitude: -46.6250
  - Distância calculada: ~1.2 km

# Resultado: Cliente está DENTRO do raio → Vídeo é baixado e reproduzido
```

### Cálculo de Distância

O sistema usa a fórmula de **Geodésica** (geopy) para calcular a distância real entre dois pontos na Terra, considerando a curvatura do planeta.

```python
from geopy.distance import geodesic

cliente = (-23.5600, -46.6250)
video = (-23.5505, -46.6333)
distancia = geodesic(cliente, video).kilometers
# Resultado: 1.2 km
```

## 📡 API Endpoints

### Públicos

#### `GET /api/timestamp`
Retorna o timestamp da última atualização no servidor.

**Resposta:**
```json
{
  "last_update": "2025-11-06T13:45:30.123456",
  "timestamp": 1699281930
}
```

#### `GET /api/videos?latitude=<lat>&longitude=<lon>`
Retorna lista de vídeos disponíveis para a localização fornecida.

**Parâmetros:**
- `latitude`: Float (-90 a 90)
- `longitude`: Float (-180 a 180)

**Resposta:**
```json
{
  "videos": [
    {
      "id": 1,
      "filename": "20251106_134530_propaganda.mp4",
      "original_filename": "propaganda.mp4",
      "latitude": -23.5505,
      "longitude": -46.6333,
      "radius_km": 5.0,
      "uploaded_at": "2025-11-06T13:45:30.123456"
    }
  ],
  "count": 1
}
```

#### `GET /api/download/<video_id>`
Baixa um vídeo específico.

**Resposta:**
- Arquivo de vídeo (download)

### Admin (Requer Login)

#### `GET /admin/login`
Página de login do admin.

#### `GET /admin/`
Dashboard do admin com lista de vídeos e formulário de upload.

#### `POST /admin/upload`
Upload de novo vídeo com informações de geolocalização.

**Form Data:**
- `video`: Arquivo de vídeo
- `latitude`: Float
- `longitude`: Float
- `radius_km`: Float

#### `POST /admin/delete/<video_id>`
Deleta um vídeo do sistema.

#### `GET /admin/download-client`
Baixa o executável do cliente (client.exe).

#### `GET /admin/logout`
Logout do admin.

## 🔧 Tecnologias Utilizadas

### Backend (Servidor)
| Tecnologia | Versão | Função |
|------------|--------|--------|
| Python | 3.x | Linguagem principal |
| Flask | 3.0.0 | Framework web |
| SQLAlchemy | 3.1.1 | ORM para banco de dados |
| Flask-WTF | 1.2.1 | Formulários e validação |
| GeoPy | 2.4.1 | Cálculos geográficos |
| Werkzeug | 3.0.1 | Utilitários web |
| Python-dotenv | 1.0.0 | Variáveis de ambiente |

### Frontend (Admin)
| Tecnologia | Versão | Função |
|------------|--------|--------|
| Bootstrap | 5.3.0 | Interface UI |
| Bootstrap Icons | 1.11.1 | Ícones |

### Cliente
| Tecnologia | Versão | Função |
|------------|--------|--------|
| Requests | 2.31.0 | HTTP client |
| OpenCV | 4.10.0.84 | Reprodução de vídeo |
| NumPy | < 2.0 | Dependência do OpenCV |

## 📁 Estrutura de Arquivos

```
sistema_de_propaganda/
│
├── 📄 README.md                 # Documentação básica
├── 📄 SISTEMA.md                # Este arquivo (documentação técnica)
├── 📄 requirements.txt          # Dependências Python
├── 📄 .gitignore               # Arquivos ignorados pelo Git
├── 📄 descricao.txt            # Descrição original do projeto
│
├── 📁 server/                   # Backend Flask
│   ├── 📄 app.py               # Aplicação principal
│   ├── 📄 config.py            # Configurações
│   ├── 📄 models.py            # Modelos do banco de dados
│   ├── 📄 routes.py            # Rotas da API e Admin
│   ├── 📄 forms.py             # Formulários WTForms
│   ├── 📄 utils.py             # Funções auxiliares
│   ├── 📄 .env                 # Variáveis de ambiente
│   ├── 📄 propaganda.db        # Banco de dados SQLite
│   ├── 📁 templates/           # Templates HTML
│   │   ├── 📄 admin.html      # Dashboard admin
│   │   └── 📄 login.html      # Página de login
│   └── 📁 uploads/             # Vídeos armazenados
│       └── 📹 [arquivos de vídeo]
│
└── 📁 client/                   # Cliente Python
    ├── 📄 client.py            # Aplicação principal
    ├── 📄 config.py            # Configurações
    ├── 📄 .env                 # Variáveis de ambiente
    ├── 📄 client.exe           # Executável compilado (opcional)
    ├── 📄 last_timestamp.txt   # Último timestamp verificado
    └── 📁 videos/              # Vídeos baixados
        └── 📹 [arquivos de vídeo]
```

## ⚙️ Configuração

### Servidor (server/.env)

```env
SECRET_KEY=sua-chave-secreta-segura-aqui
ADMIN_PASSWORD=senha-do-admin
DATABASE_URI=sqlite:///propaganda.db
UPLOAD_FOLDER=uploads
```

### Cliente (client/.env)

```env
# URL do servidor
SERVER_URL=http://localhost:5000

# Localização do cliente
CLIENT_LATITUDE=-23.5505
CLIENT_LONGITUDE=-46.6333

# Intervalo de verificação em segundos (300 = 5 minutos)
CHECK_INTERVAL=300
```

## 🚀 Instalação e Execução

### 1. Instalar Dependências

```powershell
# Ativar ambiente virtual (se existir)
.\venv\Scripts\Activate.ps1

# Instalar dependências
pip install -r requirements.txt
```

### 2. Configurar Variáveis de Ambiente

Edite os arquivos `.env` do servidor e cliente conforme necessário.

### 3. Iniciar o Servidor

```powershell
cd server
python app.py
```

Servidor estará disponível em: `http://localhost:5000`

### 4. Acessar o Admin

1. Navegue para: `http://localhost:5000/admin/login`
2. Digite a senha configurada no `.env`
3. Faça upload de vídeos com suas localizações

### 5. Iniciar o Cliente

```powershell
cd client
python client.py
```

**Controles:**
- `q` - Sair do cliente
- `s` - Pular vídeo atual

## 🎯 Casos de Uso

### Caso 1: Propaganda Regional
```
Cenário: Loja com múltiplas filiais
- Cada filial tem vídeos específicos
- Cliente na Filial A só vê propagandas da Filial A
- Cliente na Filial B só vê propagandas da Filial B
```

### Caso 2: Eventos Localizados
```
Cenário: Show em um estádio
- Vídeos promocionais só aparecem perto do estádio
- Raio: 2 km do centro do estádio
- Clientes fora do raio não recebem o vídeo
```

### Caso 3: Campanhas por Bairro
```
Cenário: Rede de restaurantes
- Cada bairro tem ofertas específicas
- Cliente no Bairro X vê ofertas do Bairro X
- Atualização automática quando cliente muda de bairro
```

## 🔒 Segurança

### Autenticação
- Painel admin protegido por senha
- Sessões com cookies seguros
- SECRET_KEY para criptografia de sessão

### Validação
- Validação de tipos de arquivo (apenas vídeos)
- Validação de coordenadas geográficas
- Proteção contra SQL injection (SQLAlchemy ORM)
- Nomes de arquivo sanitizados

### Recomendações para Produção
1. Use HTTPS (SSL/TLS)
2. Troque SECRET_KEY e ADMIN_PASSWORD
3. Use banco de dados robusto (PostgreSQL/MySQL)
4. Configure firewall e rate limiting
5. Use autenticação mais robusta (OAuth, JWT)

## 📊 Banco de Dados

### Tabela: videos

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | Integer | Primary Key |
| filename | String(255) | Nome do arquivo no servidor |
| original_filename | String(255) | Nome original do arquivo |
| latitude | Float | Latitude do ponto central |
| longitude | Float | Longitude do ponto central |
| radius_km | Float | Raio em quilômetros |
| uploaded_at | DateTime | Data/hora do upload |

### Tabela: system_status

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | Integer | Primary Key |
| last_update | DateTime | Timestamp da última atualização |

## 🎨 Interface Admin

### Dashboard
- **Informações do Sistema**
  - Última atualização
  - Total de vídeos
  - Botão para download do client.exe

- **Upload de Vídeo**
  - Seleção de arquivo
  - Latitude e longitude
  - Raio em km
  - Validação em tempo real

- **Lista de Vídeos**
  - Tabela com todos os vídeos
  - Informações de localização
  - Botão de deletar
  - Ordenado por data (mais recente primeiro)

## 🔄 Sincronização

### Mecanismo de Timestamp
1. Cada upload/delete atualiza `system_status.last_update`
2. Cliente verifica timestamp a cada 5 minutos
3. Se timestamp mudou, cliente busca novos vídeos
4. Cliente salva timestamp local em `last_timestamp.txt`

### Fluxo de Sincronização
```
Cliente → GET /api/timestamp
        ← { "last_update": "2025-11-06T14:00:00" }

Se timestamp diferente do salvo localmente:
  Cliente → GET /api/videos?lat=-23.5505&lon=-46.6333
          ← { "videos": [...] }
  
  Para cada vídeo:
    Cliente → GET /api/download/1
            ← [arquivo de vídeo]
  
  Salvar novo timestamp localmente
```

## 📹 Formatos de Vídeo Suportados

- MP4 (recomendado)
- AVI
- MOV
- MKV
- WEBM

**Recomendação:** Use MP4 com codec H.264 para melhor compatibilidade.

## 🐛 Troubleshooting

### Problema: Cliente não baixa vídeos
**Soluções:**
- Verifique se o servidor está rodando
- Confirme as coordenadas no `client/.env`
- Verifique se há vídeos dentro do raio
- Veja os logs no terminal do cliente

### Problema: Vídeos não reproduzem
**Soluções:**
- Verifique se OpenCV está instalado: `pip install opencv-python`
- Teste com formato MP4
- Verifique se o arquivo não está corrompido

### Problema: Erro de NumPy/OpenCV
**Solução:**
```powershell
pip uninstall opencv-python numpy -y
pip install "numpy<2" opencv-python
```

### Problema: Admin não carrega
**Soluções:**
- Verifique se Flask está instalado
- Confirme porta 5000 disponível
- Veja logs de erro no terminal do servidor

## 📈 Melhorias Futuras

### Backend
- [ ] Autenticação JWT para API
- [ ] Múltiplos usuários admin
- [ ] Analytics de visualizações
- [ ] CDN para distribuição de vídeos
- [ ] Suporte a streaming (HLS/DASH)
- [ ] API de estatísticas

### Cliente
- [ ] Interface gráfica de configuração
- [ ] Auto-update do cliente
- [ ] Modo offline avançado
- [ ] Suporte a playlists
- [ ] Transições entre vídeos
- [ ] Telemetria de reprodução

### Geolocalização
- [ ] Polígonos customizados (não apenas círculos)
- [ ] Múltiplas zonas por vídeo
- [ ] Horários específicos de exibição
- [ ] Priorização de vídeos

## 📝 Licença

Este projeto é open source para fins educacionais.

## 👥 Contribuindo

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## 📞 Suporte

Para dúvidas ou problemas:
1. Verifique a seção de Troubleshooting
2. Revise os logs de erro
3. Consulte a documentação da API
4. Abra uma issue no GitHub

---

**Desenvolvido com ❤️ para propaganda digital baseada em localização**
