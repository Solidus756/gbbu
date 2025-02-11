import logging
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.crypto import get_random_string
from .models import Streamer, UserProfile, StaffApplication, Tag, StaffPosition
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.urls import reverse
from django.conf import settings

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=Streamer)
def create_user_for_streamer(sender, instance, created, **kwargs):
    if created and not instance.user:
        user = User.objects.create_user(
            username=instance.twitch_name,
            email=instance.email,
            password=get_random_string(length=8)
        )
        instance.user = user
        instance.save()

@receiver(post_save, sender=Streamer)
def send_validation_email(sender, instance, **kwargs):
    if instance.validated_by_admin and instance.user:
        token = default_token_generator.make_token(instance.user)
        uid = urlsafe_base64_encode(force_bytes(instance.user.pk))
        reset_link = f"http://{settings.ALLOWED_HOSTS[0]}{reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})}"
        subject = "Votre inscription a été validée"
        message = (
            f"Bonjour {instance.twitch_name},\n\n"
            f"Votre inscription a été validée.\n"
            f"Pour définir votre mot de passe, cliquez sur ce lien :\n{reset_link}\n\n"
            "Merci et bienvenue !"
        )
        send_mail(subject, message, "no-reply@charitystreaming.com", [instance.email])

logger = logging.getLogger(__name__)

@receiver(post_save, sender=StaffApplication)
def add_tags_to_staff_application(sender, instance, created, **kwargs):
    """
    Ajoute automatiquement les tags suivants lorsque le statut d'une candidature est mis à jour :
    - Si le status est "staff", on ajoute le tag "Staff" et un tag correspondant au poste demandé.
    - Si le status est "reserve", on ajoute un tag au format "réserve-<poste>".
    Cette opération s'exécute après la sauvegarde et n'enlève aucun tag existant.
    """
    # On ajoute toujours les tags si le status est 'staff' ou 'reserve'
    logger.info("Signal post_save pour StaffApplication déclenché pour l'instance %s", instance)
    if instance.status == 'staff':
        # Tag "Staff"
        tag_staff, _ = Tag.objects.get_or_create(name="Staff")
        instance.tags.add(tag_staff)
        # Tag correspondant au poste demandé
        tag_poste, _ = Tag.objects.get_or_create(name=instance.poste_demande.poste)
        instance.tags.add(tag_poste)
        logger.info("Tags ajoutés pour status 'staff' : Staff, %s", instance.poste_demande.poste)
    elif instance.status == 'reserve':
        # Tag pour la réserve
        tag_reserve_name = f"réserve-{instance.poste_demande.poste}"
        tag_reserve, _ = Tag.objects.get_or_create(name=tag_reserve_name)
        instance.tags.add(tag_reserve)
        logger.info("Tag ajouté pour status 'reserve' : %s", tag_reserve_name)
