from django.db import models
from django.utils.html import format_html 
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.models import User, Group
from django.utils.timezone import now
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.core.mail.backends.smtp import EmailBackend
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import PasswordResetTokenGenerator, default_token_generator
import logging
from django.core.mail import EmailMessage

logger = logging.getLogger(__name__)

PRESENCE_CHOICES = [
    ("PR", "Présentiel"),
    ("DI", "Distanciel"),
]

SOCIAL_NETWORK_CHOICES = [
    ("twitter", "Twitter"),
    ("youtube", "YouTube"),
    ("instagram", "Instagram"),
    ("facebook", "Facebook"),
    ("tiktok", "TikTok"),
]

RESOURCES = [
    ('messagerie', 'Messagerie'),
    ('profil', 'Profil'),
    ('twitchwall', 'Twitch Wall'),
    # Ajoutez d'autres ressources ici
]

ACTIONS = [
    ('view', 'Afficher'),
    ('edit', 'Modifier'),
    ('delete', 'Supprimer'),
    # Ajoutez d'autres actions ici
]

NOTIFICATION_TYPES = [
    ('info', 'Info'),
    ('alert', 'Alerte'),
    ('event', 'Événement'),
]


class StaffPosition(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Staff(models.Model):
    username = models.CharField(max_length=50, unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    position = models.ForeignKey(StaffPosition, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.username} ({self.position if self.position else 'No Position'})"

class Streamer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='streamer_profile')
    twitch_name = models.CharField(max_length=100, unique=True)
    email = models.EmailField(blank=True)
    description = models.TextField(blank=True)
    presence_mode = models.CharField(
        max_length=2,
        choices=PRESENCE_CHOICES,
        default="DI",
    )
    validated_by_admin = models.BooleanField(default=False)
    discord = models.CharField(max_length=100)
    broadcaster_type = models.CharField(max_length=50, blank=True)
    follower_count = models.PositiveIntegerField(default=0)
    profile_image_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.twitch_name

    @staticmethod
    def validate_streamer(request, streamer_id):
        """Valide un streamer et envoie un email."""
        streamer = get_object_or_404(Streamer, id=streamer_id)
        streamer.validated_by_admin = True
        streamer.save()

        # Envoi de l'email
        send_mail(
            'Bienvenue à notre événement',
            f'Bonjour {streamer.twitch_name}, votre inscription est validée.',
            'test@forestt.run',
            [streamer.email],
            fail_silently=False,
        )

        messages.success(request, 'Le streamer a été validé et un email a été envoyé.')
        return redirect('admin_dashboard')

@receiver(post_save, sender=Streamer)
def create_user_for_streamer(sender, instance, created, **kwargs):
    if created and not instance.user:
        user = User.objects.create_user(
            username=instance.twitch_name,
            email=instance.email,
            password=get_random_string(length=8)  # Temporary password
        )
        instance.user = user
        instance.save()

@receiver(post_save, sender=Streamer)
def send_validation_email(sender, instance, created, **kwargs):
    from .utils import send_dynamic_email
    logger.info(f"Signal déclenché pour le streamer : {instance.twitch_name}")
    if instance.validated_by_admin:
        # Vérifiez si un utilisateur est lié, sinon créez-le
        if not instance.user:
            user = User.objects.create_user(
                username=instance.twitch_name,
                email=instance.email,
                password=None  # L'utilisateur devra définir un mot de passe
            )
            instance.user = user
            instance.save()

        # Générer un lien de réinitialisation de mot de passe
        token = default_token_generator.make_token(instance.user)
        uid = urlsafe_base64_encode(force_bytes(instance.user.pk))
        reset_link = f"https://gb.intradc.ovh/reset/{uid}/{token}/"

        # Construire l'email
        subject = "Validation de votre inscription"
        message = (
            f"Bonjour {instance.twitch_name},\n\n"
            f"Votre inscription a été validée avec succès !\n\n"
            f"Pour accéder à votre espace utilisateur, veuillez définir votre mot de passe en cliquant sur le lien suivant :\n"
            f"{reset_link}\n\n"
            f"Merci et bienvenue parmi nous !"
        )
        from_email = "test@forestt.run"
        recipient_list = [instance.email]

        # Envoyer l'email
        send_dynamic_email(subject, message, from_email, recipient_list)

class SocialAccount(models.Model):
    streamer = models.ForeignKey(Streamer, on_delete=models.CASCADE, related_name="social_accounts")
    network = models.CharField(max_length=20, choices=SOCIAL_NETWORK_CHOICES)
    username = models.CharField(max_length=100)

    url = models.URLField(blank=True)

    def __str__(self):
        return f"{self.network} - {self.username}"

    def save(self, *args, **kwargs):
        """
        Générer un url en fonction du network + username.
        Ex : Twitter => https://twitter.com/<username>
        """
        if self.network == "twitter":
            self.url = f"https://twitter.com/{self.username}"
        elif self.network == "youtube":
            self.url = f"https://youtube.com/@{self.username}"
        elif self.network == "instagram":
            self.url = f"https://instagram.com/{self.username}"
        elif self.network == "facebook":
            self.url = f"https://facebook.com/{self.username}"
        elif self.network == "tiktok":
            self.url = f"https://www.tiktok.com/@{self.username}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.network.capitalize()} - {self.username}"        

# Message Model
class Message(models.Model):
    from_user = models.ForeignKey(User, related_name="sent_messages", on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name="received_messages", on_delete=models.CASCADE)
    subject = models.CharField(max_length=255)
    body = models.TextField()
    read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(default=now)

    def __str__(self):
        return f"{self.subject} (de {self.from_user.username} à {self.to_user.username})"

# Config SMTP
class SMTPConfig(models.Model):
    host = models.CharField(max_length=255, verbose_name="Serveur SMTP")
    port = models.PositiveIntegerField(verbose_name="Port SMTP", default=587)
    username = models.CharField(max_length=255, verbose_name="Nom d'utilisateur")
    password = models.CharField(max_length=255, verbose_name="Mot de passe")
    use_tls = models.BooleanField(default=True, verbose_name="Utiliser TLS")
    use_ssl = models.BooleanField(default=False, verbose_name="Utiliser SSL")

    def __str__(self):
        return f"Configuration SMTP ({self.host}:{self.port})"

# Config ACL
# Choix pour les ressources et actions
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

class Notification(models.Model):
    ICON_CLASSES = {
        'info': 'fa-circle-info text-primary',
        'event': 'fa-calendar-days text-success',
        'alert': 'fa-triangle-exclamation text-warning',
    }
    
    title = models.CharField(max_length=255)
    message = models.TextField()
    type = models.CharField(max_length=10, choices=NOTIFICATION_TYPES, default='info')
    recipient_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="notifications")
    recipient_group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True, blank=True, related_name="group_notifications")
    created_at = models.DateTimeField(default=now)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.get_type_display()} - {self.title}"

    class Meta:
        ordering = ['-created_at']
