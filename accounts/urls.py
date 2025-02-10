from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.public_registration, name='public_registration'),
    path('register/streamer/', views.register_streamer, name='register_streamer'),
    #path('register/staff/', views.register_staff, name='register_staff'),
    path('login/', views.user_login, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='accounts:login'), name='logout'),
    path('dashboard/', views.user_dashboard, name='dashboard'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
]
