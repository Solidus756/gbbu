from django.urls import path
from . import views

app_name = 'twitch'

urlpatterns = [
    path('wall/', views.twitch_wall, name='twitch_wall'),
]
