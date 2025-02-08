from django import forms
from django.forms import modelform_factory, inlineformset_factory
from .models import Streamer, Staff, StaffPosition, SocialAccount, Message

class StreamerForm(forms.ModelForm):
    presence_mode = forms.ChoiceField(
        choices=[("PR", "Présentiel"), ("DI", "Distanciel")],
        widget=forms.RadioSelect(attrs={"class": "form-check-inline"}),
        label="Mode de présence"
    )

    class Meta:
        model = Streamer
        fields = ["twitch_name", "email", "description", "presence_mode", "discord", "profile_image_url"]
        widgets = {
            "twitch_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Entrez votre nom Twitch"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "Entrez votre email"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "discord": forms.TextInput(attrs={"class": "form-control", "placeholder": "Votre pseudo Discord"}),
            "profile_image_url": forms.TextInput(attrs={"class": "form-control", "placeholder": "URL image de profil"}),
        }
    def clean_twitch_name(self):
        tw_name = self.cleaned_data.get('twitch_name')

        if not tw_name:
            return tw_name  # Pas de souci si vide (ou c'est déjà "required")

        # Vérifie si un autre Streamer a déjà ce nom, en excluant le cas où on édite
        # le streamer actuel (si c'est une modif)
        qs = Streamer.objects.filter(twitch_name=tw_name)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise forms.ValidationError(
                "Ce nom Twitch est déjà pris. Veuillez en choisir un autre."
            )

        return tw_name

SocialAccountFormSet = inlineformset_factory(
    Streamer,
    SocialAccount,
    fields=["network", "username"],
    extra=1,
    can_delete=True,
    widgets={
        'network': forms.Select(attrs={'class': 'form-control'}),
        'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom d’utilisateur'}),
    }
)

class StaffForm(forms.ModelForm):
    class Meta:
        model = Staff
        fields = ['username', 'first_name', 'last_name', 'email', 'position']

# Formulaire pour ajouter un poste (dans l'admin superuser par exemple)
class StaffPositionForm(forms.ModelForm):
    class Meta:
        model = StaffPosition
        fields = ['name']

# Formulaire de messagerie
class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ["to_user", "subject", "body"]
        widgets = {
            "to_user": forms.Select(attrs={"class": "form-control"}),
            "subject": forms.TextInput(attrs={"class": "form-control"}),
            "body": forms.Textarea(attrs={"class": "form-control", "rows": 5}),
        }