# Sistema de Propaganda com Geolocalização

Sistema completo de exibição de vídeos publicitários baseado em geolocalização, com portal para clientes, sistema de créditos prepagos e aprovação administrativa.

## 🚀 Funcionalidades

### Para Administradores
- ✅ Upload de vídeos com localização e raio de exibição
- ✅ Aprovação/reprovação de vídeos enviados por clientes
- ✅ Gerenciamento de pagamentos
- ✅ Adição de créditos aos vídeos
- ✅ Pausar/retomar exibição de vídeos
- ✅ Visualização de estatísticas detalhadas
- ✅ Exclusão de vídeos

### Para Clientes
- ✅ Registro e login no sistema
- ✅ Upload de vídeos para aprovação
- ✅ Visualização de status (aprovado/pago/pausado)
- ✅ Acompanhamento de créditos restantes
- ✅ Estatísticas de visualizações por vídeo
- ✅ Dashboard pessoal

### Para Visualizadores (Web Client)
- ✅ Exibição automática de vídeos baseada em localização
- ✅ Interface fullscreen com controles auto-hide
- ✅ Reprodução sequencial em loop
- ✅ Download inteligente (apenas novos vídeos)
- ✅ Detecção automática de GPS

## 📋 Requisitos

- Python 3.7+
- Navegador moderno com suporte a geolocalização
- Conexão com a internet

## 🔧 Instalação

1. **Instale as dependências:**
```bash
pip install -r requirements.txt
```

2. **Configure as variáveis de ambiente (opcional):**

Crie um arquivo `.env` na pasta `server/`:
```env
SECRET_KEY=sua_chave_secreta_aqui
ADMIN_USERNAME=admin
ADMIN_PASSWORD=senha_admin
```

3. **Inicie o servidor:**
```bash
cd server
python app.py
```

O servidor estará disponível em: `http://localhost:5050`

## 📱 Uso

### Acesso Admin
1. Acesse: `http://localhost:5050/admin/login`
2. Login padrão: `admin` / `admin123`
3. Gerencie vídeos e clientes pelo dashboard

### Portal do Cliente
1. Acesse: `http://localhost:5050/cliente/register`
2. Registre-se com seus dados
3. Faça login em: `http://localhost:5050/cliente/login`
4. Upload de vídeos e acompanhe status

### Web Client (Visualizador)
1. Acesse: `http://localhost:5050/client`
2. Clique em "Configurações"
3. Configure localização (ou use GPS)
4. Salve e aguarde os vídeos

## 🎯 Sistema de Créditos

### Fluxo Completo
1. **Upload**: Cliente envia vídeo → status: pendente
2. **Aprovação**: Admin aprova → status: aprovado
3. **Pagamento**: Admin marca como pago → status: pago
4. **Créditos**: Admin adiciona créditos (1 crédito = 1 visualização)
5. **Exibição**: Vídeo entra em exibição automaticamente
6. **Consumo**: Cada visualização consome 1 crédito
7. **Pausa Automática**: Sem créditos → vídeo pausado

### Estados do Vídeo
- **⏳ Pendente**: Aguardando aprovação
- **✓ Aprovado**: Aprovado pelo admin
- **💰 Pago**: Pagamento confirmado
- **▶️ Ativo**: Sendo exibido (créditos > 0)
- **⏸ Pausado**: Sem créditos ou pausado manualmente

## 🗂️ Estrutura do Projeto

```
sistema_de_propaganda/
├── server/
│   ├── app.py                      # Aplicação Flask
│   ├── models.py                   # Modelos BD
│   ├── forms.py                    # Formulários
│   ├── routes.py                   # Rotas API
│   ├── config.py                   # Configurações
│   ├── utils.py                    # Utilitários
│   ├── templates/
│   │   ├── admin.html              # Dashboard admin
│   │   ├── admin_login.html        # Login admin
│   │   ├── client.html             # Web client
│   │   └── cliente/
│   │       ├── login.html          # Login cliente
│   │       ├── register.html       # Registro
│   │       ├── dashboard.html      # Dashboard
│   │       └── video_stats.html    # Estatísticas
│   ├── static/
│   │   ├── css/
│   │   │   └── client.css
│   │   └── js/
│   │       └── client.js           # Lógica web client
│   └── uploads/                    # Vídeos
├── requirements.txt
└── README.md
```

## 🔐 API Endpoints

### Públicos
- `GET /api/videos` - Lista vídeos por localização
- `GET /api/download/<video_id>` - Download do vídeo
- `POST /api/visualizacao/<video_id>` - Registra visualização

### Admin (autenticação necessária)
- `POST /admin/upload` - Upload de vídeo
- `POST /admin/delete/<video_id>` - Deletar
- `POST /admin/aprovar/<video_id>` - Aprovar
- `POST /admin/reprovar/<video_id>` - Reprovar
- `POST /admin/marcar-pago/<video_id>` - Marcar pago
- `POST /admin/adicionar-creditos/<video_id>` - Adicionar créditos
- `POST /admin/pausar/<video_id>` - Pausar/retomar

### Cliente (autenticação necessária)
- `POST /cliente/login` - Login
- `POST /cliente/register` - Registro
- `GET /cliente/dashboard` - Dashboard
- `POST /cliente/upload` - Upload vídeo
- `GET /cliente/video/<video_id>/stats` - Estatísticas

## 📊 Banco de Dados

### Tabelas
- **system_status**: Status do sistema
- **clientes**: Dados dos clientes
- **videos**: Informações dos vídeos
- **logs_visualizacao**: Registro de visualizações

### Campos Principais - Video
- `aprovado`: Aprovado pelo admin (boolean)
- `pago`: Pagamento confirmado (boolean)
- `creditos`: Créditos disponíveis (integer)
- `pausado`: Vídeo pausado (boolean)
- `visualizacoes`: Total de views (integer)
- `cliente_id`: FK para clientes (NULL = admin)

## 🛠️ Tecnologias

- **Flask 3.0.0** - Framework web
- **SQLAlchemy 3.1.1** - ORM
- **Flask-WTF 1.2.1** - Formulários
- **GeoPy 2.4.1** - Geolocalização
- **Werkzeug 3.0.1** - Segurança
- **Bootstrap 5.3.0** - UI
- **OpenCV 4.10.0.84** - Vídeo (client desktop)
- **NumPy <2** - Compatibilidade

## 🔒 Segurança

- Senhas com hash (Werkzeug)
- Sessões Flask
- CSRF protection
- Validação de uploads
- Sanitização de inputs

## 🐛 Troubleshooting

### NumPy Error
```bash
pip install "numpy<2"
```

### Geolocation Denied
Habilite permissões no navegador

### Vídeos Não Aparecem
Verifique:
1. ✓ Aprovado?
2. ✓ Pago?
3. ✓ Créditos > 0?
4. ✓ Não pausado?
5. ✓ Dentro do raio?

### BD Corrompido
Delete `propaganda.db` e reinicie

## 📈 Recursos Futuros

- [ ] Relatórios PDF
- [ ] Gráficos de visualização
- [ ] Gateway de pagamento
- [ ] Notificações email
- [ ] App mobile
- [ ] Sistema de cupons
- [ ] Multi-idiomas

## 📄 Licença

Projeto proprietário. Todos os direitos reservados.
