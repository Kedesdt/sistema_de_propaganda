# 📺 Sistema de Propaganda - Cliente

Cliente Python para exibição de propagandas (vídeos e imagens) em tela cheia, baseado em geolocalização.

## 📋 Requisitos

- **Python 3.8 ou superior**
- **Webcam ou monitor** para exibição
- **Conexão com a internet** para comunicação com o servidor

### Dependências do Sistema

#### Windows

- Nenhuma dependência adicional necessária

#### Linux (Ubuntu/Debian)

```bash
sudo apt-get update
sudo apt-get install python3 python3-pip python3-venv
sudo apt-get install python3-opencv  # Opcional, acelera instalação
```

#### Linux (Fedora/RHEL)

```bash
sudo dnf install python3 python3-pip
```

#### macOS

```bash
brew install python3
```

## 🚀 Instalação e Execução

### Windows

1. **Baixe a pasta `client`** com todos os arquivos
2. **Execute o script**:

   ```cmd
   run.bat
   ```

   Ou com URL do servidor:

   ```cmd
   run.bat http://seu-servidor.com:5050
   ```

### Linux/macOS

1. **Baixe a pasta `client`** com todos os arquivos
2. **Dê permissão de execução**:
   ```bash
   chmod +x run.sh
   ```
3. **Execute o script**:

   ```bash
   ./run.sh
   ```

   Ou com URL do servidor:

   ```bash
   ./run.sh http://seu-servidor.com:5050
   ```

## ⚙️ Configuração

### Primeira Execução

Na primeira vez, o sistema solicitará:

1. **URL do Servidor** (ou pressione Enter para usar padrão)
   - Exemplo: `http://192.168.1.100:5050`

### Arquivo de Configuração

Edite o arquivo `config.py` para configurar:

```python
SERVER_URL = "http://localhost:5050"  # URL do servidor
CLIENT_LATITUDE = -23.550520           # Latitude do cliente
CLIENT_LONGITUDE = -46.633308          # Longitude do cliente
CHECK_INTERVAL = 60                    # Intervalo de verificação (segundos)
```

## 🎮 Controles

Durante a reprodução:

- **`Q`** - Encerrar o cliente
- **`S`** - Pular para próxima mídia

## 📁 Estrutura de Arquivos

```
client/
├── client.py           # Aplicação principal
├── config.py           # Configurações
├── requirements.txt    # Dependências Python
├── run.bat            # Script de execução (Windows)
├── run.sh             # Script de execução (Linux/macOS)
└── README.md          # Este arquivo
```

## 🔄 Como Funciona

1. **Conexão**: Cliente conecta ao servidor e envia sua localização
2. **Busca**: Servidor retorna mídias (vídeos/imagens) disponíveis para aquela região
3. **Download**: Cliente baixa as mídias localmente
4. **Reprodução**: Exibe em tela cheia em loop contínuo
5. **Impressões**: Registra cada visualização no servidor (consome créditos)
6. **Atualização**: Verifica periodicamente por novas mídias

### Tipos de Mídia Suportados

- **Vídeos**: MP4, AVI, MOV, MKV, WEBM
- **Imagens**: JPG, JPEG, PNG, GIF, WEBP (30 segundos cada)

## 🐛 Solução de Problemas

### "Python não encontrado"

Instale Python 3.8+ de https://www.python.org/ (Windows) ou use o gerenciador de pacotes do seu sistema (Linux/macOS).

### "Erro ao instalar dependências"

**Linux**: Instale bibliotecas de desenvolvimento:

```bash
sudo apt-get install python3-dev build-essential
```

### "Não foi possível conectar ao servidor"

Verifique:

- URL do servidor está correta
- Servidor está rodando
- Firewall não está bloqueando a porta
- Rede está funcionando

### "Nenhuma mídia disponível"

- Verifique se há vídeos aprovados e pagos no servidor
- Confirme se a localização do cliente está correta
- Verifique o raio de alcance dos vídeos cadastrados

## 📊 Logs

O cliente exibe logs detalhados no terminal:

- ✅ Conexão estabelecida
- 📥 Download de mídias
- ▶️ Reprodução iniciada
- 📊 Impressões registradas
- 🔄 Verificações de atualização

## 🔐 Segurança

- Comunicação via HTTP/HTTPS
- Não armazena credenciais
- Mídias temporárias em pasta local
- Limpeza automática de arquivos antigos

## 📞 Suporte

Para problemas ou dúvidas, contate o administrador do sistema.

---

**Versão**: 1.0.0  
**Última atualização**: Dezembro 2025
