from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

from charity_streaming.views import home

urlpatterns = [
    path('', home, name='home'),  # Route pour la racine
    path('admin/', admin.site.urls),
    path('jet/', include(('jet.urls', 'jet'), namespace='jet')),
    path('jet/dashboard/', include(('jet.dashboard.urls', 'jet-dashboard'), namespace='jet-dashboard')),
    path('accounts/', include('accounts.urls')),
    path('twitch/', include('twitch.urls')),
    path('notifications/', include('notifications.urls')),
    path('acl/', include('acl.urls')),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)