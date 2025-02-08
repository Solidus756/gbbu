from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from charity_streaming import view

urlpatterns = [
    path('', views.home, name='home'),  # Route pour la racine
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('twitch/', include('twitch.urls')),
    path('notifications/', include('notifications.urls')),
    path('acl/', include('acl.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)