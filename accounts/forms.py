from django import forms
from django.contrib.auth.models import User
from django.forms import inlineformset_factory
from .models import Streamer, Tag, UserProfile, SocialAccount, StaffApplication, StaffPosition


class StreamerForm(forms.ModelForm):
    class Meta:
        model = Streamer
        fields = ['twitch_name', 'email', 'description', 'discord', 'profile_image_url', 'presence_mode']
        widgets = {
            'profile_image_url': forms.HiddenInput(),
            'presence_mode': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def clean_twitch_name(self):
        tw_name = self.cleaned_data.get('twitch_name', '').strip()
        # Vérification insensible à la casse pour éviter les doublons
        if self.instance.pk:
            qs = Streamer.objects.filter(twitch_name__iexact=tw_name).exclude(pk=self.instance.pk)
        else:
            qs = Streamer.objects.filter(twitch_name__iexact=tw_name)
        if qs.exists():
            raise forms.ValidationError("Ce streamer est déjà enregistré.")
        return tw_name

class StaffApplicationForm(forms.ModelForm):
    class Meta:
        model = StaffApplication
        fields = ['pseudo', 'pseudo_discord', 'pseudo_twitch', 'email', 'poste_demande', 'pourquoi', 'tags']
        widgets = {
            'pseudo': forms.TextInput(attrs={'class': 'form-control'}),
            'pseudo_discord': forms.TextInput(attrs={'class': 'form-control'}),
            'pseudo_twitch': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'poste_demande': forms.Select(attrs={'class': 'form-control'}),
            'pourquoi': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'tags': forms.HiddenInput(),  # Champ caché pour préserver les tags
        }




class UserProfileForm(forms.ModelForm):
    tags = forms.CharField(required=False, help_text="Séparez les tags par une virgule. Les nouveaux tags seront créés automatiquement.")
    
    class Meta:
        model = UserProfile
        fields = ['tags']
    
    def clean_tags(self):
        tags_str = self.cleaned_data.get('tags', '')
        tag_list = [tag.strip() for tag in tags_str.split(',') if tag.strip()]
        return tag_list

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
