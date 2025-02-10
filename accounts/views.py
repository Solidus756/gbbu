from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail
from django.urls import reverse
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group, User
from .forms import StreamerForm, StaffApplicationForm, UserProfileForm, SocialAccountFormSet
from .models import Streamer, UserProfile, Tag

def register_streamer(request):
    if request.method == "POST":
        form = StreamerForm(request.POST)
        if form.is_valid():
            streamer = form.save(commit=False)
            streamer.save()
            # Le signal va créer automatiquement l'utilisateur associé si nécessaire.
            if streamer.user:
                streamer.user.groups.add(Group.objects.get(name="Streamer"))
            messages.success(request, "Inscription streamer réussie.")
            return redirect('accounts:login')
    else:
        form = StreamerForm()
    return render(request, "accounts/register_streamer.html", {"form": form})

'''
def register_staff(request):
    if request.method == "POST":
        form = StaffForm(request.POST)
        if form.is_valid():
            staff = form.save(commit=False)
            staff.save()
            if staff.user:
                staff.user.groups.add(Group.objects.get(name="Staff"))
            messages.success(request, "Inscription staff réussie.")
            return redirect('accounts:login')
    else:
        form = StaffForm()
    return render(request, "accounts/register_staff.html", {"form": form})
'''
def user_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            if user.is_superuser or user.groups.filter(name__in=["Admin", "Staff"]).exists():
                return redirect('/admin/')
            return redirect('accounts:dashboard')
        else:
            messages.error(request, "Identifiants invalides.")
    return render(request, "accounts/login.html")

@login_required
def user_dashboard(request):
    profile = getattr(request.user, 'profile', None)
    context = {'user': request.user, 'profile': profile}
    return render(request, "accounts/dashboard.html", context)

@login_required
def profile_edit(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            tag_names = form.cleaned_data['tags']
            profile.tags.clear()
            for tag_name in tag_names:
                tag, _ = Tag.objects.get_or_create(name=tag_name)
                profile.tags.add(tag)
            profile.save()
            messages.success(request, "Profil mis à jour avec succès.")
            return redirect('accounts:dashboard')
        else:
            messages.error(request, "Erreur lors de la mise à jour du profil.")
    else:
        existing_tags = ", ".join([tag.name for tag in profile.tags.all()])
        form = UserProfileForm(instance=profile, initial={'tags': existing_tags})
    return render(request, "accounts/profile_edit.html", {"form": form})

def public_registration(request):
    if request.method == "POST":
        registration_type = request.POST.get("registration_type")
        if registration_type == "streamer":
            streamer_form = StreamerForm(request.POST)
            social_formset = SocialAccountFormSet(request.POST, prefix="socialaccount_set")
            if streamer_form.is_valid() and social_formset.is_valid():
                streamer = streamer_form.save(commit=False)
                streamer.save()
                social_formset.instance = streamer
                social_formset.save()
                # Envoi d'un email de confirmation
                send_mail(
                    "Demande d'inscription reçue",
                    f"Bonjour {streamer.twitch_name},\n\nVotre demande d'inscription en tant que streamer a bien été reçue. Vous recevrez un email de confirmation dès qu'un organisateur aura validé votre inscription.",
                    "no-reply@charitystreaming.com",
                    [streamer.email],
                )
                messages.success(request, "Votre demande d'inscription a été envoyée.")
                return redirect("home")
            else:
                messages.error(request, "Veuillez corriger les erreurs dans le formulaire Streamer.")
                staff_form = StaffApplicationForm()  # pour recharger l'autre formulaire
        elif registration_type == "staff":
            staff_form = StaffApplicationForm(request.POST)
            if staff_form.is_valid():
                staff_application = staff_form.save(commit=False)
                staff_application.save()
                send_mail(
                    "Demande d'inscription reçue",
                    f"Bonjour {staff_application.pseudo},\n\nVotre demande d'inscription en tant que staff a bien été reçue. Vous recevrez un email de confirmation dès qu'un organisateur aura validé votre inscription.",
                    "no-reply@charitystreaming.com",
                    [staff_application.email],
                )
                messages.success(request, "Votre demande d'inscription a été envoyée.")
                return redirect("home")
            else:
                messages.error(request, "Veuillez corriger les erreurs dans le formulaire Staff.")
                streamer_form = StreamerForm()
                social_formset = SocialAccountFormSet(prefix="socialaccount_set")
        else:
            messages.error(request, "Veuillez choisir un type d'inscription.")
            streamer_form = StreamerForm()
            staff_form = StaffApplicationForm()
            social_formset = SocialAccountFormSet(prefix="socialaccount_set")
    else:
        streamer_form = StreamerForm()
        staff_form = StaffApplicationForm()
        social_formset = SocialAccountFormSet(prefix="socialaccount_set")
    return render(request, "accounts/public_registration.html", {
        'streamer_form': streamer_form,
        'staff_form': staff_form,
        'social_formset': social_formset,
    })

def home(request):
    streamer_form = StreamerForm()
    staff_form = StaffApplicationForm()
    social_formset = SocialAccountFormSet(prefix="socialaccount_set")
    return render(request, 'home.html', {
        'streamer_form': streamer_form,
        'staff_form': staff_form,
        'social_formset': social_formset,
    })