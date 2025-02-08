from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('dashboard/', views.user_notifications, name='dashboard'),
    path('mark_read/<int:notification_id>/', views.mark_notification_as_read, name='mark_notification_as_read'),
]
