from django.db import models
from django.contrib.auth.models import User, Group
from django.utils import timezone

NOTIFICATION_TYPES = [
    ('info', 'Info'),
    ('alert', 'Alerte'),
    ('event', 'Événement'),
]

class Notification(models.Model):
    title = models.CharField(max_length=255)
    message = models.TextField()
    type = models.CharField(max_length=10, choices=NOTIFICATION_TYPES, default='info')
    # Destinataire : un utilisateur, un groupe ou un tag (ici, pour le tag, nous le gérerons via UserProfile tags)
    recipient_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="notifications")
    recipient_group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True, blank=True, related_name="group_notifications")
    # Pour les tags, nous stockons le nom du tag à titre indicatif
    recipient_tag = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_type_display()} - {self.title}"
