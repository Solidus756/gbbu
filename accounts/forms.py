from django import forms
from django.contrib.auth.models import User
from .models import Streamer, Staff, Tag, UserProfile


class StreamerForm(forms.ModelForm):
    class Meta:
        model = Streamer
        fields = ['twitch_name', 'email', 'description', 'discord', 'profile_image_url']
        widgets = {
            'profile_image_url': forms.HiddenInput(),
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

class StaffForm(forms.ModelForm):
    class Meta:
        model = Staff
        fields = ['first_name', 'last_name', 'email']

class UserProfileForm(forms.ModelForm):
    tags = forms.CharField(required=False, help_text="Séparez les tags par une virgule. Les nouveaux tags seront créés automatiquement.")
    
    class Meta:
        model = UserProfile
        fields = ['tags']
    
    def clean_tags(self):
        tags_str = self.cleaned_data.get('tags', '')
        tag_list = [tag.strip() for tag in tags_str.split(',') if tag.strip()]
        return tag_list
