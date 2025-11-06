# Sistema de Propaganda com Geolocalização

Sistema completo de propaganda digital baseado em localização geográfica, composto por servidor Flask e cliente Python.

## 📋 Características

- **Servidor Flask**:
  - API REST para gerenciamento de vídeos
  - Painel administrativo protegido por senha
  - Upload de vídeos com geolocalização (latitude, longitude e raio)
  - Banco de dados SQLite com SQLAlchemy
  - Sistema de timestamp para sincronização

- **Cliente Python**:
  - Verifica atualizações a cada 5 minutos
  - Baixa automaticamente vídeos disponíveis para sua localização
  - Reproduz vídeos em fullscreen em loop
  - Usa OpenCV para reprodução de vídeo

## 🚀 Instalação

### 1. Instalar dependências

```powershell
pip install -r requirements.txt
```

### 2. Configurar o Servidor

Edite o arquivo `server/.env`:

```env
SECRET_KEY=sua-chave-secreta-segura
ADMIN_PASSWORD=sua-senha-admin
DATABASE_URI=sqlite:///propaganda.db
UPLOAD_FOLDER=uploads
```

### 3. Configurar o Cliente

Edite o arquivo `client/.env`:

```env
SERVER_URL=http://localhost:5000
CLIENT_LATITUDE=-23.5505
CLIENT_LONGITUDE=-46.6333
CHECK_INTERVAL=300
```

**Importante**: Ajuste as coordenadas (CLIENT_LATITUDE e CLIENT_LONGITUDE) para a localização real onde o cliente será executado.

## 🎯 Como Usar

### Iniciar o Servidor

```powershell
cd server
python app.py
```

O servidor estará disponível em: http://localhost:5000

### Acessar o Admin

1. Acesse: http://localhost:5000/admin/login
2. Use a senha configurada no `.env` (padrão: `admin123`)
3. Faça upload de vídeos com suas respectivas localizações

### Iniciar o Cliente

```powershell
cd client
python client.py
```

O cliente irá:
1. Verificar vídeos disponíveis para sua localização
2. Baixar os vídeos necessários
3. Reproduzir em loop fullscreen
4. Verificar atualizações a cada 5 minutos

**Controles durante reprodução**:
- `q` - Sair do cliente
- `s` - Pular vídeo atual

## 🗺️ Sistema de Geolocalização

Cada vídeo possui:
- **Latitude**: Coordenada geográfica (-90 a 90)
- **Longitude**: Coordenada geográfica (-180 a 180)
- **Raio (km)**: Distância em quilômetros a partir do ponto central

O cliente só baixa e reproduz vídeos que estão dentro do raio de sua localização.

### Exemplo

Se um vídeo está configurado para:
- Latitude: -23.5505
- Longitude: -46.6333
- Raio: 10 km

Apenas clientes localizados dentro de um raio de 10 km desse ponto irão reproduzir o vídeo.

## 📁 Estrutura do Projeto

```
sistema_de_propaganda/
├── server/
│   ├── app.py              # Aplicação principal Flask
│   ├── config.py           # Configurações
│   ├── models.py           # Modelos do banco de dados
│   ├── routes.py           # Rotas da API e Admin
│   ├── forms.py            # Formulários WTForms
│   ├── utils.py            # Funções auxiliares
│   ├── .env                # Variáveis de ambiente
│   ├── templates/
│   │   ├── admin.html      # Dashboard admin
│   │   └── login.html      # Página de login
│   └── uploads/            # Vídeos armazenados
│
├── client/
│   ├── client.py           # Cliente principal
│   ├── config.py           # Configurações do cliente
│   ├── .env                # Variáveis de ambiente
│   └── videos/             # Vídeos baixados
│
├── requirements.txt        # Dependências Python
└── README.md              # Este arquivo
```

## 🔧 API Endpoints

### Públicos

- `GET /` - Informações da API
- `GET /api/timestamp` - Retorna timestamp da última atualização
- `GET /api/videos?latitude=X&longitude=Y` - Lista vídeos disponíveis
- `GET /api/download/<video_id>` - Baixa um vídeo específico

### Admin (Requer autenticação)

- `GET /admin/login` - Página de login
- `GET /admin/` - Dashboard admin
- `POST /admin/upload` - Upload de novo vídeo
- `POST /admin/delete/<video_id>` - Deletar vídeo
- `GET /admin/logout` - Logout

## 🛠️ Tecnologias Utilizadas

### Servidor
- Flask - Framework web
- SQLAlchemy - ORM para banco de dados
- WTForms - Validação de formulários
- GeoPy - Cálculos de geolocalização
- Bootstrap 5 - Interface administrativa

### Cliente
- Requests - Requisições HTTP
- OpenCV (cv2) - Reprodução de vídeo
- Python-dotenv - Gerenciamento de variáveis de ambiente

## 📝 Formatos de Vídeo Suportados

- MP4
- AVI
- MOV
- MKV
- WEBM

## ⚙️ Configurações Avançadas

### Alterar intervalo de verificação

No arquivo `client/.env`, ajuste:
```env
CHECK_INTERVAL=300  # Segundos (300 = 5 minutos)
```

### Aumentar limite de upload

No arquivo `server/config.py`:
```python
MAX_CONTENT_LENGTH = 500 * 1024 * 1024  # 500 MB
```

### Usar banco de dados externo

No arquivo `server/.env`:
```env
DATABASE_URI=postgresql://user:pass@localhost/dbname
```

## 🐛 Solução de Problemas

### Servidor não inicia
- Verifique se a porta 5000 está disponível
- Confirme se todas as dependências foram instaladas
- Verifique logs de erro no console

### Cliente não baixa vídeos
- Confirme que o servidor está rodando
- Verifique se as coordenadas estão corretas
- Confirme que existem vídeos cadastrados no raio da localização

### Vídeos não reproduzem
- Verifique se o OpenCV está instalado corretamente
- Confirme que os arquivos de vídeo não estão corrompidos
- Teste com diferentes formatos de vídeo

## 📄 Licença

Este projeto é de código aberto para fins educacionais.

## 👤 Autor

Desenvolvido como sistema de propaganda digital com geolocalização.
