from django.db import models
from django.contrib.auth.models import Group, User

# Exemple de ressources et actions – vous pouvez les étendre
RESOURCES = [
    ('twitch_wall', 'Twitch Wall'),
    ('smtp_config', 'Configuration SMTP'),
    ('admin_dashboard', 'Dashboard Admin'),
]

ACTIONS = [
    ('view', 'Afficher'),
    ('edit', 'Modifier'),
    ('delete', 'Supprimer'),
]

class ACLRule(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, verbose_name="Groupe")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Utilisateur")
    resource = models.CharField(max_length=50, choices=RESOURCES, verbose_name="Ressource")
    action = models.CharField(max_length=50, choices=ACTIONS, verbose_name="Action")
    
    class Meta:
        unique_together = ("group", "user", "resource", "action")
    
    def __str__(self):
        target = f"User: {self.user}" if self.user else f"Group: {self.group}"
        return f"{target} -> {self.resource} ({self.action})"
