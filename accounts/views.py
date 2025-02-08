from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group, User
from .forms import StreamerForm, StaffForm, UserProfileForm
from .models import Streamer, Staff, UserProfile, Tag

def register_streamer(request):
    if request.method == "POST":
        form = StreamerForm(request.POST)
        if form.is_valid():
            streamer = form.save(commit=False)
            streamer.save()
            # Le signal dans signals.py créera automatiquement le User associé si besoin
            # Ajout dans le groupe "Streamer"
            if streamer.user:
                streamer.user.groups.add(Group.objects.get(name="Streamer"))
            messages.success(request, "Inscription streamer réussie.")
            return redirect('accounts:login')
    else:
        form = StreamerForm()
    return render(request, "accounts/register_streamer.html", {"form": form})

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

def user_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            # Redirection selon rôle (exemple simple)
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
    # Pour simplifier, on édite uniquement le UserProfile (créé automatiquement par signal)
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            tag_names = form.cleaned_data['tags']
            # Clear existing tags et ajouter ceux saisis
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
        # Pré-remplir le champ tags avec une chaîne séparée par des virgules
        existing_tags = ", ".join([tag.name for tag in profile.tags.all()])
        form = UserProfileForm(instance=profile, initial={'tags': existing_tags})
    return render(request, "accounts/profile_edit.html", {"form": form})
