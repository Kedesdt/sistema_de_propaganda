"""
Documentação da API com Swagger/OpenAPI
"""
from flasgger import Swagger, swag_from


# Configuração do Swagger
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'apispec',
            "route": '/apispec.json',
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/api/docs"
}

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "Sistema de Propaganda API",
        "description": "API para gerenciamento de propagandas com geolocalização",
        "version": "1.0.0",
        "contact": {
            "name": "Sistema de Propaganda",
            "url": "http://localhost:5050"
        }
    },
    "host": "localhost:5050",
    "basePath": "/",
    "schemes": [
        "http",
        "https"
    ],
    "tags": [
        {
            "name": "API",
            "description": "Endpoints da API REST"
        },
        {
            "name": "Admin",
            "description": "Endpoints administrativos"
        },
        {
            "name": "Cliente",
            "description": "Endpoints do portal do cliente"
        }
    ]
}


def init_swagger(app):
    """Inicializa o Swagger no app"""
    return Swagger(app, config=swagger_config, template=swagger_template)


# Specs para cada endpoint
timestamp_spec = {
    "tags": ["API"],
    "summary": "Obter timestamp da última atualização",
    "description": "Retorna o timestamp da última modificação no sistema",
    "responses": {
        "200": {
            "description": "Timestamp retornado com sucesso",
            "schema": {
                "type": "object",
                "properties": {
                    "last_update": {
                        "type": "string",
                        "format": "date-time",
                        "example": "2025-11-07T17:44:32.839000"
                    },
                    "timestamp": {
                        "type": "integer",
                        "example": 1699385072
                    }
                }
            }
        }
    }
}

get_videos_spec = {
    "tags": ["API"],
    "summary": "Listar vídeos disponíveis",
    "description": "Retorna lista de vídeos disponíveis para uma localização específica",
    "parameters": [
        {
            "name": "latitude",
            "in": "query",
            "type": "number",
            "required": True,
            "description": "Latitude da localização (-90 a 90)",
            "example": -23.5505
        },
        {
            "name": "longitude",
            "in": "query",
            "type": "number",
            "required": True,
            "description": "Longitude da localização (-180 a 180)",
            "example": -46.6333
        }
    ],
    "responses": {
        "200": {
            "description": "Lista de vídeos retornada com sucesso",
            "schema": {
                "type": "object",
                "properties": {
                    "videos": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "integer"},
                                "filename": {"type": "string"},
                                "latitude": {"type": "number"},
                                "longitude": {"type": "number"},
                                "radius_km": {"type": "number"},
                                "creditos": {"type": "integer"},
                                "visualizacoes": {"type": "integer"}
                            }
                        }
                    },
                    "count": {
                        "type": "integer",
                        "example": 5
                    }
                }
            }
        },
        "400": {
            "description": "Parâmetros inválidos",
            "schema": {
                "type": "object",
                "properties": {
                    "error": {
                        "type": "string",
                        "example": "Latitude e longitude são obrigatórios"
                    }
                }
            }
        }
    }
}

download_video_spec = {
    "tags": ["API"],
    "summary": "Download de vídeo",
    "description": "Faz o download de um vídeo específico pelo ID",
    "parameters": [
        {
            "name": "video_id",
            "in": "path",
            "type": "integer",
            "required": True,
            "description": "ID do vídeo",
            "example": 1
        }
    ],
    "responses": {
        "200": {
            "description": "Arquivo de vídeo",
            "schema": {
                "type": "file"
            }
        },
        "404": {
            "description": "Vídeo não encontrado"
        }
    }
}

registrar_visualizacao_spec = {
    "tags": ["API"],
    "summary": "Registrar visualização",
    "description": "Registra uma visualização de vídeo e consome 1 crédito",
    "parameters": [
        {
            "name": "video_id",
            "in": "path",
            "type": "integer",
            "required": True,
            "description": "ID do vídeo",
            "example": 1
        },
        {
            "name": "body",
            "in": "body",
            "schema": {
                "type": "object",
                "properties": {
                    "latitude": {
                        "type": "number",
                        "description": "Latitude do cliente (opcional)",
                        "example": -23.5505
                    },
                    "longitude": {
                        "type": "number",
                        "description": "Longitude do cliente (opcional)",
                        "example": -46.6333
                    }
                }
            }
        }
    ],
    "responses": {
        "200": {
            "description": "Visualização registrada com sucesso",
            "schema": {
                "type": "object",
                "properties": {
                    "success": {
                        "type": "boolean",
                        "example": True
                    },
                    "creditos_restantes": {
                        "type": "integer",
                        "example": 99
                    },
                    "pausado": {
                        "type": "boolean",
                        "example": False
                    },
                    "visualizacoes_total": {
                        "type": "integer",
                        "example": 1
                    }
                }
            }
        },
        "402": {
            "description": "Sem créditos disponíveis",
            "schema": {
                "type": "object",
                "properties": {
                    "error": {
                        "type": "string",
                        "example": "Vídeo sem créditos"
                    },
                    "creditos": {
                        "type": "integer",
                        "example": 0
                    },
                    "pausado": {
                        "type": "boolean",
                        "example": True
                    }
                }
            }
        },
        "403": {
            "description": "Vídeo pausado ou não aprovado",
            "schema": {
                "type": "object",
                "properties": {
                    "error": {
                        "type": "string",
                        "example": "Vídeo pausado"
                    }
                }
            }
        }
    }
}
