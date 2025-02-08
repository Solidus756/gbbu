from django import forms
from .models import Notification
from django.contrib.auth.models import Group, User
from accounts.models import Tag

class NotificationForm(forms.ModelForm):
    recipient_choice = forms.ChoiceField(
        choices=[('user', 'Utilisateur'), ('group', 'Groupe'), ('tag', 'Tag')],
        label="Type de destinataire",
        widget=forms.RadioSelect
    )
    recipient_value = forms.CharField(label="Destinataire", help_text="Saisissez l'identifiant de l'utilisateur, le nom du groupe ou du tag")
    
    class Meta:
        model = Notification
        fields = ['title', 'message', 'type']
