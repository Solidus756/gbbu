import requests

from django.shortcuts import render
from django.http import JsonResponse
from accounts.models import Streamer, BlacklistedStreamer
from django.conf import settings
from .utils import get_twitch_token

def twitch_wall(request):
    token = get_twitch_token()
    twitch_data = []
    streamers = Streamer.objects.filter(validated_by_admin=True).order_by('twitch_name')
    for streamer in streamers:
        headers = {
            'Client-ID': settings.TWITCH_CLIENT_ID,
            'Authorization': f'Bearer {token}',
        }
        url = f"https://api.twitch.tv/helix/streams?user_login={streamer.twitch_name}"
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json().get('data', [])
            if data:
                stream = data[0]
                thumbnail = stream.get('thumbnail_url', '').replace('{width}', '320').replace('{height}', '180')
                twitch_data.append({
                    'twitch_name': streamer.twitch_name,
                    'status': 'Online',
                    'viewers': stream.get('viewer_count', 0),
                    'thumbnail': thumbnail,
                    'game_name': stream.get('game_name', 'Inconnu'),
                    'title': stream.get('title', 'Sans titre'),
                })
            else:
                twitch_data.append({
                    'twitch_name': streamer.twitch_name,
                    'status': 'Offline',
                    'viewers': 0,
                    'thumbnail': '/static/images/offline.png',
                })
        else:
            twitch_data.append({
                'twitch_name': streamer.twitch_name,
                'status': 'Error',
                'viewers': 0,
                'thumbnail': '/static/images/error.png',
            })
    return render(request, 'twitch/twitch_wall.html', {'twitch_data': twitch_data})

def ajax_fetch_streamer_info(request):
    twitch_name = request.GET.get('twitch_name', '').strip()
    if not twitch_name:
        return JsonResponse({'error': 'Aucun nom Twitch fourni.'}, status=400)
    
    normalized_name = twitch_name.lower()
    
    # Vérifier si le streamer est déjà enregistré (insensible à la casse)
    if Streamer.objects.filter(twitch_name__iexact=normalized_name).exists():
        return JsonResponse({'error': 'Ce streamer est déjà enregistré.'}, status=400)
    
    # Vérifier si le nom est dans la blacklist
    if BlacklistedStreamer.objects.filter(twitch_name__iexact=normalized_name).exists():
        return JsonResponse({'error': "Une erreur s'est produite, réessayez plus tard."}, status=400)
    
    token = get_twitch_token()
    if not token:
        return JsonResponse({'error': "Impossible de récupérer le token Twitch."}, status=500)
    
    headers = {
        'Client-ID': settings.TWITCH_CLIENT_ID,
        'Authorization': f'Bearer {token}',
    }
    url = f"https://api.twitch.tv/helix/users?login={normalized_name}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json().get('data', [])
        if data:
            user_info = data[0]
            description = user_info.get('description', '')
            profile_image_url = user_info.get('profile_image_url', '')
            return JsonResponse({
                'description': description,
                'profile_image_url': profile_image_url,
            })
        else:
            return JsonResponse({'error': "Aucune information trouvée pour ce nom."}, status=404)
    else:
        return JsonResponse({'error': "Erreur lors de la récupération des informations."}, status=500)