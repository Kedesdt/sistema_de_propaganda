"""
Rotas da API REST
"""
from flask import Blueprint, request, jsonify, send_from_directory, current_app
from models import SystemStatus
from services import VideoService

api_bp = Blueprint('api', __name__, url_prefix='/api')


@api_bp.route('/timestamp', methods=['GET'])
def get_timestamp():
    """Retorna o timestamp da última atualização"""
    last_update = SystemStatus.get_last_update()
    return jsonify({
        'last_update': last_update.isoformat(),
        'timestamp': int(last_update.timestamp())
    })


@api_bp.route('/videos', methods=['GET'])
def get_videos():
    """
    Retorna lista de vídeos disponíveis para a localização do cliente
    Apenas vídeos aprovados, pagos e não pausados
    Parâmetros: latitude, longitude
    """
    try:
        latitude = float(request.args.get('latitude'))
        longitude = float(request.args.get('longitude'))
    except (TypeError, ValueError):
        return jsonify({'error': 'Latitude e longitude são obrigatórios'}), 400
    
    # Buscar vídeos disponíveis para a localização
    available_videos = VideoService.get_videos_by_location(latitude, longitude)
    
    return jsonify({
        'videos': [video.to_dict() for video in available_videos],
        'count': len(available_videos)
    })


@api_bp.route('/download/<int:video_id>', methods=['GET'])
def download_video(video_id):
    """Baixa um vídeo específico"""
    from models import Video
    video = Video.query.get_or_404(video_id)
    return send_from_directory(
        current_app.config['UPLOAD_FOLDER'],
        video.filename,
        as_attachment=True,
        download_name=video.original_filename
    )


@api_bp.route('/visualizacao/<int:video_id>', methods=['POST'])
def registrar_visualizacao(video_id):
    """
    Registra visualização de um vídeo e consome 1 crédito
    Parâmetros JSON: latitude, longitude (opcionais)
    """
    data = request.get_json() or {}
    
    success, message, video = VideoService.registrar_visualizacao(
        video_id=video_id,
        ip_address=request.remote_addr,
        latitude=data.get('latitude'),
        longitude=data.get('longitude')
    )
    
    if success:
        return jsonify({
            'success': True,
            'creditos_restantes': video.creditos,
            'pausado': video.pausado,
            'visualizacoes_total': video.visualizacoes
        })
    else:
        status_code = 403 if 'pausado' in message.lower() or 'aprovado' in message.lower() else 402
        return jsonify({
            'error': message,
            'creditos': video.creditos if video else 0,
            'pausado': video.pausado if video else True
        }), status_code
