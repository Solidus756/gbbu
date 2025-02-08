from django.urls import path
from django.conf.urls import include
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import PasswordResetConfirmView, LogoutView
from django.conf import settings
from django.conf.urls.static import static

from . import views
from .views import password_reset_confirm, user_notifications, mark_notification_as_read
from .custom_admin import my_admin_site


urlpatterns = [
    path('', views.home, name='home'),
    path('register/streamer/', views.register_streamer, name='register_streamer'),
    path('register/staff/', views.register_staff, name='register_staff'),
    path('manage/positions/', views.manage_positions, name='manage_positions'),
    path('twitchwall/', views.twitch_wall, name='twitch_wall'),
#    path('myadmin/', include((custom_admin_urls, 'myadmin'), namespace='myadmin')),
    path('myadmin/', my_admin_site.urls),
    path('ajax/fetch_twitch_info/', views.fetch_twitch_info, name='fetch_twitch_info'),
    path('ajax/check_twitch_name/', views.check_twitch_name, name='check_twitch_name'),
    path("inbox/", views.inbox, name="inbox"),
    path("sentbox/", views.sentbox, name="sentbox"),
    path("compose/", views.compose_message, name="compose_message"),
    path("acl/", views.manage_acl, name="manage_acl"),
    path('login/', views.user_login, name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('user/dashboard/', views.user_dashboard, name='user_dashboard'),
    path('user/notifications/', views.user_notifications, name='notifications'),
    path('notification/<int:notification_id>/', views.view_notification, name='view_notification'),
    path('notifications/<int:notification_id>/read/', views.mark_notification_as_read, name='mark_notification_as_read'),
    path('user/profile/', views.user_profile, name='user_profile'),
    path('user/profile/edit/', views.profile_edit, name='profile_edit'),
    path('reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'), name='password_reset_complete'),
    path('jet/', include('jet.urls', 'jet')),  # URLs de Django JET
    path('jet/dashboard/', include('jet.dashboard.urls', 'jet-dashboard')),  # Django JET dashboard URLS
    
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
