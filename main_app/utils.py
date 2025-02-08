from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.urls import reverse
from django.core.mail.backends.smtp import EmailBackend

from .views import password_reset_confirm
from .models import SMTPConfig

def send_password_reset_email(user):
    # Générer le jeton de réinitialisation et le lien
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    reset_link = reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})

    # Construire le lien absolu
    full_reset_link = f"http://{settings.DOMAIN_NAME}{reset_link}"

    # Préparer le contenu de l'email
    subject = "Créer votre mot de passe"
    message = render_to_string('emails/password_reset_email.html', {
        'user': user,
        'reset_link': full_reset_link,
    })

    # Envoyer l'email
    email = EmailMessage(subject, message, to=[user.email])
    email.send()

def send_dynamic_email(subject, message, from_email, recipient_list):
    # Charger la configuration SMTP depuis la base de données
    smtp_config = SMTPConfig.objects.first()
    if not smtp_config:
        raise ValueError("Aucune configuration SMTP disponible.")

    # Configurer le backend avec les paramètres de la base de données
    email_backend = EmailBackend(
        host=smtp_config.host,
        port=smtp_config.port,
        username=smtp_config.username,
        password=smtp_config.password,
        use_tls=smtp_config.use_tls,
        use_ssl=smtp_config.use_ssl,
    )

    # Envoyer l'email
    email = EmailMessage(subject, message, from_email, recipient_list, connection=email_backend)
    email.send()