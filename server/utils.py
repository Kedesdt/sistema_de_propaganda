from geopy.distance import geodesic

def is_within_radius(client_lat, client_lon, video_lat, video_lon, radius_km):
    """
    Verifica se o cliente está dentro do raio do vídeo
    """
    client_location = (client_lat, client_lon)
    video_location = (video_lat, video_lon)
    distance = geodesic(client_location, video_location).kilometers
    return distance <= radius_km

def get_videos_for_location(videos, client_lat, client_lon):
    """
    Retorna lista de vídeos que estão dentro do raio da localização do cliente
    """
    available_videos = []
    for video in videos:
        if is_within_radius(client_lat, client_lon, video.latitude, video.longitude, video.radius_km):
            available_videos.append(video)
    return available_videos
