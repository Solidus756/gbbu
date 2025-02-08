from django import forms
from django.contrib.auth.models import User
from .models import Streamer, Staff, Tag, UserProfile

class StreamerForm(forms.ModelForm):
    class Meta:
        model = Streamer
        fields = ['twitch_name', 'email', 'description', 'presence_mode', 'discord', 'profile_image_url']
    
    def clean_twitch_name(self):
        tw_name = self.cleaned_data.get('twitch_name')
        qs = Streamer.objects.filter(twitch_name=tw_name)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Ce nom Twitch est déjà pris. Veuillez en choisir un autre.")
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
