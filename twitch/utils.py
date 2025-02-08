import requests
from django.core.cache import cache
from django.conf import settings

def get_twitch_token():
    token = cache.get('twitch_token')
    if token:
        return token
    url = "https://id.twitch.tv/oauth2/token"
    params = {
        "client_id": settings.TWITCH_CLIENT_ID,
        "client_secret": settings.TWITCH_SECRET,
        "grant_type": "client_credentials",
    }
    response = requests.post(url, params=params)
    if response.status_code == 200:
        data = response.json()
        token = data.get("access_token")
        expires_in = data.get("expires_in", 3600)
        cache.set('twitch_token', token, timeout=expires_in)
        return token
    return None
