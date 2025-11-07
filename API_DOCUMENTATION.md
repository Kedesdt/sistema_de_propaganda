# 📡 API REST - Sistema de Propaganda

## 🌐 Base URL

```
http://localhost:5050/api
```

## 🔒 Rate Limiting

- **Global**: 200 requests/day, 50 requests/hour
- **Videos**: 30 requests/minute
- **Download**: 10 requests/hour
- **Visualização**: Conforme créditos disponíveis

## 📚 Documentação Interativa

Acesse a documentação Swagger em:
```
http://localhost:5050/api/docs
```

## 🔑 Autenticação

A maioria dos endpoints não requer autenticação. Para endpoints administrativos, use sessão do Flask.

---

## 📋 Endpoints

### 1. Get Timestamp

Obtém o timestamp da última atualização do sistema.

**Endpoint:** `GET /api/timestamp`

**Response:**
```json
{
  "last_update": "2025-11-07T17:44:32.839000",
  "timestamp": 1699385072
}
```

---

### 2. Listar Vídeos

Lista vídeos disponíveis para uma localização específica.

**Endpoint:** `GET /api/videos`

**Query Parameters:**
- `latitude` (required): Latitude da localização (-90 a 90)
- `longitude` (required): Longitude da localização (-180 a 180)

**Exemplo:**
```bash
curl "http://localhost:5050/api/videos?latitude=-23.5505&longitude=-46.6333"
```

**Response 200:**
```json
{
  "videos": [
    {
      "id": 1,
      "filename": "20251107_174432_video.mp4",
      "original_filename": "video.mp4",
      "latitude": -23.5505,
      "longitude": -46.6333,
      "radius_km": 50.0,
      "creditos": 100,
      "visualizacoes": 10,
      "aprovado": true,
      "pago": true,
      "pausado": false
    }
  ],
  "count": 1
}
```

**Response 400:**
```json
{
  "error": "Latitude e longitude são obrigatórios"
}
```

---

### 3. Download de Vídeo

Faz o download de um vídeo específico.

**Endpoint:** `GET /api/download/<video_id>`

**Path Parameters:**
- `video_id` (required): ID do vídeo

**Exemplo:**
```bash
curl -O "http://localhost:5050/api/download/1"
```

**Response 200:**
- Arquivo de vídeo (binary)

**Response 404:**
```json
{
  "error": "Vídeo não encontrado"
}
```

---

### 4. Registrar Visualização

Registra uma visualização de vídeo e consome 1 crédito.

**Endpoint:** `POST /api/visualizacao/<video_id>`

**Path Parameters:**
- `video_id` (required): ID do vídeo

**Request Body (optional):**
```json
{
  "latitude": -23.5505,
  "longitude": -46.6333
}
```

**Exemplo:**
```bash
curl -X POST "http://localhost:5050/api/visualizacao/1" \
  -H "Content-Type: application/json" \
  -d '{"latitude": -23.5505, "longitude": -46.6333}'
```

**Response 200:**
```json
{
  "success": true,
  "creditos_restantes": 99,
  "pausado": false,
  "visualizacoes_total": 11
}
```

**Response 402 (Sem créditos):**
```json
{
  "error": "Vídeo sem créditos",
  "creditos": 0,
  "pausado": true
}
```

**Response 403 (Vídeo pausado):**
```json
{
  "error": "Vídeo pausado",
  "creditos": 50,
  "pausado": true
}
```

**Response 404:**
```json
{
  "error": "Vídeo não encontrado"
}
```

---

## 🔄 Fluxo de Uso Típico

### Cliente de Vídeo

1. **Obter timestamp** para verificar atualizações
2. **Listar vídeos** disponíveis na localização atual
3. **Download de vídeos** necessários
4. **Registrar visualização** ao exibir o vídeo

```python
import requests

# 1. Verificar atualizações
response = requests.get('http://localhost:5050/api/timestamp')
timestamp = response.json()['timestamp']

# 2. Buscar vídeos
params = {'latitude': -23.5505, 'longitude': -46.6333}
response = requests.get('http://localhost:5050/api/videos', params=params)
videos = response.json()['videos']

# 3. Download do vídeo
if videos:
    video_id = videos[0]['id']
    response = requests.get(f'http://localhost:5050/api/download/{video_id}')
    with open('video.mp4', 'wb') as f:
        f.write(response.content)
    
    # 4. Registrar visualização
    data = {'latitude': -23.5505, 'longitude': -46.6333}
    response = requests.post(
        f'http://localhost:5050/api/visualizacao/{video_id}',
        json=data
    )
    result = response.json()
    print(f"Créditos restantes: {result['creditos_restantes']}")
```

---

## ⚠️ Códigos de Erro

| Código | Descrição |
|--------|-----------|
| 200 | Sucesso |
| 400 | Bad Request - Parâmetros inválidos |
| 402 | Payment Required - Sem créditos |
| 403 | Forbidden - Vídeo pausado/não aprovado |
| 404 | Not Found - Recurso não encontrado |
| 413 | Payload Too Large - Arquivo muito grande |
| 429 | Too Many Requests - Rate limit excedido |
| 500 | Internal Server Error - Erro interno |

---

## 📊 Modelo de Dados

### Video
```typescript
{
  id: number;
  filename: string;
  original_filename: string;
  latitude: number;           // -90 a 90
  longitude: number;          // -180 a 180
  radius_km: number;          // Raio de exibição em km
  creditos: number;           // Créditos disponíveis
  visualizacoes: number;      // Total de visualizações
  aprovado: boolean;          // Aprovado pelo admin
  pago: boolean;              // Cliente pagou
  pausado: boolean;           // Vídeo pausado
  uploaded_at: string;        // ISO 8601 timestamp
  cliente_id: number | null;  // ID do cliente (null = admin)
}
```

---

## 🧪 Testando a API

### Com curl
```bash
# Timestamp
curl http://localhost:5050/api/timestamp

# Vídeos
curl "http://localhost:5050/api/videos?latitude=-23&longitude=-46"

# Visualização
curl -X POST http://localhost:5050/api/visualizacao/1 \
  -H "Content-Type: application/json" \
  -d '{"latitude": -23, "longitude": -46}'
```

### Com Python
```python
import requests

base_url = 'http://localhost:5050/api'

# Timestamp
r = requests.get(f'{base_url}/timestamp')
print(r.json())

# Vídeos
r = requests.get(f'{base_url}/videos', params={
    'latitude': -23.5505,
    'longitude': -46.6333
})
print(r.json())
```

### Com Postman/Insomnia

Importe a coleção Swagger JSON:
```
http://localhost:5050/apispec.json
```

---

## 🔐 Segurança

- Rate limiting ativo em todos os endpoints
- Validação de parâmetros obrigatória
- Logs de todas as requisições
- CORS pode ser configurado se necessário

---

## 📞 Suporte

Para dúvidas ou problemas com a API:
- Acesse `/api/docs` para documentação interativa
- Verifique os logs em `logs/propaganda.log`
- Consulte o código fonte em `routes/api.py`
