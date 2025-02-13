from django.urls import path
from . import views

app_name = 'twitch'

urlpatterns = [
    path('wall/', views.twitch_wall, name='twitch_wall'),
    path('ajax/fetch_streamer_info/', views.ajax_fetch_streamer_info, name='ajax_fetch_streamer_info'),
    path('ajax/update_streamer_info/', views.ajax_update_streamer_info, name='ajax_update_streamer_info'),
]
