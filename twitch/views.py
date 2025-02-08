from django.shortcuts import render
from accounts.models import Streamer
from django.conf import settings
from .utils import get_twitch_token
import requests

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
