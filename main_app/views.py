from django.core.mail import EmailMessage
from django.core.mail.backends.smtp import EmailBackend
from django.template.loader import render_to_string
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import Group, User
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator, PasswordResetTokenGenerator
from django.contrib.auth.forms import SetPasswordForm, UserChangeForm
from django import forms
from django.forms import modelformset_factory
from django.db import transaction

import requests

from .forms import StreamerForm, StaffForm, StaffPositionForm, SocialAccountFormSet, MessageForm
from .models import Streamer, StaffPosition, Message, ACLRule, SMTPConfig, SocialAccount, Notification


ICON_MAP = {
    'info': 'fa-circle-info text-primary',
    'event': 'fa-calendar-days text-success',
    'alert': 'fa-triangle-exclamation text-danger',
}

# Page d'accueil
def home(request):
    return render(request, 'home.html')

# Check doublon
def check_twitch_name(request):
    twitch_name = request.GET.get("username", "").strip()
    if not twitch_name:
        return JsonResponse({"error": "No username provided"}, status=400)

    exists = Streamer.objects.filter(twitch_name=twitch_name).exists()
    return JsonResponse({"exists": exists})

# Inscription Streamer
def register_streamer(request):
    if request.method == "POST":
        streamer_form = StreamerForm(request.POST)
        formset = SocialAccountFormSet(request.POST)
        if streamer_form.is_valid() and formset.is_valid():
            streamer = streamer_form.save(commit=False)
            # On ne change pas email => c’est manuel
            streamer.save()
            formset.instance = streamer
            formset.save()

             # Assigner au groupe Streamer
            streamer_user = streamer.user  # Utilisez l'attribut user lié
            streamer_group = Group.objects.get(name="Streamer")
            streamer_user.groups.add(streamer_group)

            # message de succès, redirection, etc.
            return redirect("home")
    else:
        streamer_form = StreamerForm()
        formset = SocialAccountFormSet()
    return render(request, "register_streamer.html", {
        "streamer_form": streamer_form,
        "formset": formset
    })


# Inscription Staff
def register_staff(request):
    if request.method == "POST":
        staff_form = StaffForm(request.POST)
        if staff_form.is_valid():
            staff = staff_form.save(commit=False)
            staff.save()
            
            # Assigner au groupe Staff
            staff_user = staff.user  # Utilisez l'attribut user lié
            staff_group = Group.objects.get(name="Staff")
            staff_user.groups.add(staff_group)
            
            messages.success(request, "Inscription réussie pour le staff.")
            return redirect("home")
    else:
        staff_form = StaffForm()
    return render(request, "register_staff.html", {"staff_form": staff_form})

# Gestion des positions (exemple minimal, autorisé seulement aux superusers)
@user_passes_test(lambda u: u.is_superuser)
def manage_positions(request):
    if request.method == 'POST':
        form = StaffPositionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Poste ajouté avec succès.")
            return redirect('manage_positions')
    else:
        form = StaffPositionForm()

    positions = StaffPosition.objects.all()
    context = {
        'form': form,
        'positions': positions,
    }
    return render(request, 'manage_positions.html', context)

# Twitch Wall
def get_twitch_token():
    """
    Récupère un token OAuth2 "client_credentials" de Twitch.
    Nécessite dans settings.py :
        TWITCH_CLIENT_ID = ...
        TWITCH_SECRET = ...
    """
    url = "https://id.twitch.tv/oauth2/token"
    params = {
        "client_id": settings.TWITCH_CLIENT_ID,
        "client_secret": settings.TWITCH_SECRET,
        "grant_type": "client_credentials",
    }
    response = requests.post(url, params=params)

    if response.status_code == 200:
        data = response.json()
        # data contient { "access_token": "...", "expires_in": ..., "token_type": "bearer" }
        return data["access_token"]
    else:
        # Gérez l’erreur (ex: logs) si besoin
        print("Erreur lors de la récupération du token Twitch:", response.status_code, response.text)
        return None

def twitch_wall(request):
    """
    Affiche la liste des streamers, leur statut et le nombre de viewers.
    """
    # 1) On récupère le token
    token = get_twitch_token()
    if not token:
        # En cas d'erreur, on peut soit renvoyer un message, soit ignorer
        return render(request, 'twitchwall.html', {
            'twitch_data': [],
            'error': "Impossible de récupérer un token Twitch."
        })

    # 2) On boucle sur les streamers
    streamers = Streamer.objects.filter(validated_by_admin=True).order_by('twitch_name')
    twitch_data = []

    for streamer in streamers:
        headers = {
            'Client-ID': settings.TWITCH_CLIENT_ID,
            'Authorization': f'Bearer {token}',
        }
        url = f"https://api.twitch.tv/helix/streams?user_login={streamer.twitch_name}"
        response = requests.get(url, headers=headers)
        
        print("Status:", response.status_code)
        print("Response:", response.text)

        if response.status_code == 200:
            data = response.json().get('data', [])
            if data:
                stream = data[0]
                # Construction de la miniature
                thumbnail = stream.get('thumbnail_url', '').replace('{width}', '320').replace('{height}', '180')

                # Récupération du nom de jeu et titre
                game_name = stream.get('game_name', 'Jeu inconnu')
                title = stream.get('title', 'Sans titre')

                twitch_data.append({
                    'twitch_name': streamer.twitch_name,
                    'status': 'Online',
                    'viewers': stream.get('viewer_count', 0),
                    'thumbnail': thumbnail,
                    'game_name': game_name,
                    'title': title,

                })
            else:
                # Hors ligne
                twitch_data.append({
                    'twitch_name': streamer.twitch_name,
                    'status': 'Offline',
                    'viewers': 0,
                    'thumbnail': '/static/images/offline.png',
                })
        else:
            # Erreur ou impossible de contacter l'API
            twitch_data.append({
                'twitch_name': streamer.twitch_name,
                'status': 'Error',
                'viewers': 0,
                'thumbnail': '/static/images/error.png',
            })

    return render(request, 'twitchwall.html', {'twitch_data': twitch_data})

def fetch_twitch_info(request):
    """
    Reçoit ?username=... et retourne un JSON avec email, description, broadcaster_type, follower_count, profile_image_url.
    Note: l'API Twitch Helix ne fournit généralement pas l'email 
    sauf via des scopes OAuth plus larges (non dispo en simple client_credentials).
    Mais on peut simuler en attendant, ou le laisser vide.
    """
    twitch_username = request.GET.get('username', '')
    if not twitch_username:
        return JsonResponse({'error': 'No username provided'}, status=400)
    
    # 1) Récupérer un token via client_credentials (ou le stocker en cache)
    token_data = requests.post(
        'https://id.twitch.tv/oauth2/token',
        params={
            'client_id': settings.TWITCH_CLIENT_ID,
            'client_secret': settings.TWITCH_SECRET,
            'grant_type': 'client_credentials'
        }
    ).json()
    access_token = token_data.get('access_token')
    if not access_token:
        return JsonResponse({'error': 'Could not retrieve Twitch token'}, status=500)
    
    # 2) Appeler Helix pour récupérer user info
    headers = {
        'Client-ID': settings.TWITCH_CLIENT_ID,
        'Authorization': f'Bearer {access_token}',
    }
    # Endpoint pour les infos user
    url_user = f"https://api.twitch.tv/helix/users?login={twitch_username}"
    response_user = requests.get(url_user, headers=headers)
    
    if response_user.status_code != 200:
        return JsonResponse({'error': 'API error', 'status': response_user.status_code}, status=500)
    
    user_data = response_user.json().get('data', [])
    if not user_data:
        return JsonResponse({'error': 'User not found'}, status=404)
    
    user_info = user_data[0]
    # Extraire data
    broadcaster_id = user_info.get('id', '')
    broadcaster_type = user_info.get('broadcaster_type', '')
    description = user_info.get('description', '')
    profile_image_url = user_info.get('profile_image_url', '')
    
    # 3) Récupérer le nombre de followers (endpoint séparé)
    # Helix propose /users/follows?to_id=<user_id> => renvoie data=[...], total=...
    user_id = user_info.get('id')
    url_followers = f"https://api.twitch.tv/helix/channels/followers?broadcaster_id={broadcaster_id}"
    response_follows = requests.get(url_followers, headers=headers)
    follower_count = 0
    if response_follows.status_code == 200:
        follow_data = response_follows.json()
        follower_count = follow_data.get('total', 0)
    else:
        print("Erreur followers:", response_follows.status_code, response_follows.text)
    
    # 4) Retourner tout ça au navigateur
    return JsonResponse({
        'broadcaster_type': broadcaster_type,
        'description': description,
        'profile_image_url': profile_image_url,
        'follower_count': follower_count,
    })

# Boîte de réception
@login_required
def inbox(request):
    messages_received = request.user.received_messages.all().order_by("-timestamp")
    return render(request, "messaging/inbox.html", {"messages": messages_received})

# Boîte d'envoi
@login_required
def sentbox(request):
    messages_sent = request.user.sent_messages.all().order_by("-timestamp")
    return render(request, "messaging/sentbox.html", {"messages": messages_sent})

# Rédiger un message
@login_required
def compose_message(request):
    if request.method == "POST":
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.from_user = request.user
            message.save()
            messages.success(request, "Message envoyé avec succès !")
            return redirect("inbox")
    else:
        form = MessageForm()
    return render(request, "messaging/compose.html", {"form": form})

def validate_user(user):
    # Assigner le groupe en fonction du rôle
    group = Group.objects.get(name="Streamer")  # ou "Staff"
    user.groups.add(group)

@user_passes_test(lambda u: u.is_superuser)
def manage_acl(request):
    acl_rules = ACLRule.objects.all()
    return render(request, "acl/manage_acl.html", {"acl_rules": acl_rules})

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Redirection conditionnelle selon le rôle
            if user.is_superuser:
                return redirect('/myadmin/')  # Redirige vers l'admin pour les super-admins
            elif user.groups.filter(name='Admin').exists():
                return redirect('/myadmin/')  # Admins accèdent aussi à l'admin
            else:
                return redirect('/user/dashboard/')  # Redirige les utilisateurs normaux
        else:
            return render(request, 'login.html', {'error': 'Identifiants invalides'})
    return render(request, 'login.html')

@login_required
def user_dashboard(request):
    user = request.user
    notifications = request.user.received_messages.filter(read=False)
    streamer = getattr(user, 'streamer_profile', None)  # Récupère le profil Streamer lié à l'utilisateur
    
    # Récupération des réseaux sociaux
    social_accounts = []
    if streamer:
        for account in streamer.social_accounts.all():
            social_accounts.append({
                'network': account.network,
                'username': account.username,
                'icon': f"fab fa-{account.network.lower()}",  # Génère l'icône Font Awesome
            })

    context = {
        'user': request.user,
        'notifications': notifications,
        'streamer': streamer,  # Passe le streamer au template
        'social_accounts': social_accounts,  # Passe la liste des réseaux au template
    }
    return render(request, 'user_dashboard.html', context)

def send_password_reset_email(request, user_id):
    user = get_object_or_404(User, id=user_id)
    smtp_config = SMTPConfig.objects.first()  # Récupère la configuration SMTP

    if not smtp_config:
        raise Exception("Configuration SMTP introuvable")

    # Générer un lien de réinitialisation de mot de passe
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    reset_link = request.build_absolute_uri(
        reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
    )

    # Contenu de l'email
    subject = "Créer votre mot de passe"
    message = render_to_string('emails/password_reset_email.html', {'reset_link': reset_link, 'user': user})

    # Utiliser la configuration SMTP personnalisée
    email_backend = EmailBackend(
        host=smtp_config.host,
        port=smtp_config.port,
        username=smtp_config.username,
        password=smtp_config.password,
        use_tls=smtp_config.use_tls,
        use_ssl=smtp_config.use_ssl,
    )

    # Envoyer l'email
    email = EmailMessage(subject, message, to=[user.email], connection=email_backend)
    email.send()

    messages.success(request, f"Email envoyé à {user.email}.")
    return redirect('admin_dashboard')

def password_reset_confirm(request, uidb64, token):
    token_generator = PasswordResetTokenGenerator()

    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and token_generator.check_token(user, token):
        if request.method == 'POST':
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Votre mot de passe a été défini avec succès !')
                return redirect('login')  # Redirigez vers une page de connexion appropriée
        else:
            form = SetPasswordForm(user)

        return render(request, 'password_reset_confirm.html', {'form': form})
    else:
        messages.error(request, 'Le lien de réinitialisation est invalide ou a expiré.')
        return redirect('home')  # Redirigez vers une page appropriée

@login_required
def user_notifications(request):
    notifications = Notification.objects.filter(recipient_user=request.user).order_by('-created_at')

    context = {
        'notifications': notifications,
    }

    return render(request, "user_notifications.html", context)

@login_required
def view_notification(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, recipient_user=request.user)

    return render(request, 'notification_detail.html', {'notification': notification})

@login_required
def mark_notification_as_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, recipient_user=request.user)

    if request.method == "POST":
        notification.is_read = True
        notification.save()
        messages.success(request, "Notification marquée comme lue.")

    return redirect('notifications')  # Redirection après lecture

def user_notifications(request):
    notifications = Notification.objects.filter(recipient_user=request.user).order_by('-created_at')

    for notification in notifications:
        notification.icon_class = ICON_MAP.get(notification.type, 'fa-bell text-secondary')

    return render(request, "user_notifications.html", {"notifications": notifications})
    
'''
@login_required
def profile_edit(request):
    streamer = get_object_or_404(User, username=request.user.username)
    if request.method == 'POST':
        form = StreamerEditForm(request.POST, instance=streamer)
        if form.is_valid():
            form.save()
            messages.success(request, "Profil mis à jour avec succès.")
            return redirect('user_dashboard')  # Remplacez par l'URL de redirection appropriée
    else:
        form = StreamerEditForm(instance=streamer)

    return render(request, 'profile_edit.html', {'form': form})
'''
@login_required
def profile_edit(request):
    streamer = get_object_or_404(Streamer, user=request.user)

    if request.method == 'POST':
        print("Formulaire soumis")  # Debug
        print("Données reçues :", request.POST)  # Affiche toutes les données du formulaire

        form = StreamerEditForm(request.POST, request.FILES, instance=streamer)
        social_formset = SocialAccountFormSet(request.POST or None, instance=streamer)

        print("Données du formulaire:", request.POST)  # Debug

        if form.is_valid():
            print("✅ Formulaire principal valide.")
        else:
            print("❌ Erreurs du formulaire principal :", form.errors)

        if social_formset.is_valid():
            print("✅ Formset valide.")
        else:
            print("❌ Erreurs du formset :", social_formset.errors)

        if form.is_valid() and social_formset.is_valid():
            print("💾 Sauvegarde des données...")
            form.save()
            social_formset.save()
            messages.success(request, "Profil mis à jour avec succès.")
            return redirect('user_dashboard')
        
        else:
            print("Erreurs du formulaire:", form.errors)  # Debug
            print("Erreurs du formset:", social_formset.errors)  # Debug
            messages.error(request, "Erreur lors de la sauvegarde. Vérifiez les champs.")

    else:
        form = StreamerEditForm(instance=streamer)
        social_formset = SocialAccountFormSet(instance=streamer)

    return render(request, 'profile_edit.html', {
        'form': form,
        'social_formset': social_formset,
    })

@login_required
def user_profile(request):
    user = request.user
    streamer = getattr(user, 'streamer', None)  # Récupère le profil Streamer lié à l'utilisateur
    
    # Récupère les réseaux sociaux avec leurs icônes
    social_accounts = []
    if streamer:
        for account in streamer.social_accounts.all():
            social_accounts.append({
                'network': account.network,
                'username': account.username,
                'icon': f"fa fa-{account.network.lower()}",  # Font Awesome icon
            })

    context = {
        'streamer': streamer,
        'social_accounts': social_accounts,
    }
    return render(request, 'user_profile.html', context)

class StreamerEditForm(forms.ModelForm):
    class Meta:
        model = Streamer
        fields = ['twitch_name','email', 'discord', 'presence_mode']  # Champs autorisés à la modification
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['twitch_name'].disabled = True
        self.fields['email'].widget.attrs.update({'placeholder': 'Votre email'})
        self.fields['discord'].widget.attrs.update({'placeholder': 'Votre pseudo Discord'})
        self.fields['presence_mode'].widget.attrs.update({'placeholder': 'Mode de présence'})

@login_required
def user_dashboard(request):
    streamer = getattr(request.user, 'streamer_profile', None)  # ✅ Récupérer le profil du streamer
    notifications = Notification.objects.filter(recipient_user=request.user).order_by('-created_at')
    notifications_unread_count = notifications.filter(is_read=False).count()
    
    context = {
        'user': request.user,
        'streamer': streamer,  # ✅ Ajout du profil du streamer
        'social_accounts': streamer.social_accounts.all() if streamer else None,  # ✅ Ajout des réseaux sociaux
        'notifications': notifications,  # ✅ Toutes les notifications
        'notifications_unread_count': notifications_unread_count,
    }
    
    return render(request, 'user_dashboard.html', context)


@login_required
def profile_edit(request):
    # Récupération du profil Streamer lié à l'utilisateur
    streamer = get_object_or_404(Streamer, user=request.user)

    # Initialisation du formulaire principal et du formset
    if request.method == 'POST':
        form = StreamerEditForm(request.POST, instance=streamer)
        social_formset = SocialAccountFormSet(request.POST, instance=streamer)
        
        # Validation des deux formulaires
        if form.is_valid() and social_formset.is_valid():
            form.save()
            social_formset.save()
            messages.success(request, "Profil mis à jour avec succès.")
            return redirect('user_dashboard')
    else:
        form = StreamerEditForm(instance=streamer)
        social_formset = SocialAccountFormSet(instance=streamer)

    # Rendu de la page avec les formulaires
    return render(request, 'profile_edit.html', {
        'form': form,
        'social_formset': social_formset,
    })

def notifications_context(request):
    if request.user.is_authenticated:
        notifications = Notification.objects.filter(recipient_user=request.user).order_by('-created_at')
        notifications_unread_count = notifications.filter(is_read=False).count()
    else:
        notifications = []
        notifications_unread_count = 0

    return {
        'notifications': notifications,  # Toutes les notifications (limitées dans le template)
        'notifications_unread_count': notifications_unread_count,  # Compteur de non lues
    }
