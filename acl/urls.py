from django.urls import path
from . import views

app_name = 'acl'

urlpatterns = [
    # Une vue de gestion des ACL accessible aux superusers
    path('manage/', views.manage_acl, name='manage_acl'),
]
