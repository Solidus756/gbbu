from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

PRESENCE_CHOICES = [
    ("PR", "Présentiel"),
    ("DI", "Distanciel"),
]

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return self.name

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    tags = models.ManyToManyField(Tag, blank=True)
    
    def __str__(self):
        return f"Profile de {self.user.username}"

class Streamer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='streamer_profile')
    twitch_name = models.CharField(max_length=100, unique=True)
    email = models.EmailField(blank=True)
    description = models.TextField(blank=True)
    presence_mode = models.CharField(max_length=2, choices=PRESENCE_CHOICES, default="DI")
    validated_by_admin = models.BooleanField(default=False)
    discord = models.CharField(max_length=100, blank=True)
    broadcaster_type = models.CharField(max_length=50, blank=True)
    follower_count = models.PositiveIntegerField(default=0)
    profile_image_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.twitch_name

class Staff(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='staff_profile')
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    # Vous pouvez ajouter d'autres champs spécifiques au staff ici
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
