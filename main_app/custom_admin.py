import logging
logger = logging.getLogger(__name__)

from django.contrib import admin
from django.core.mail import send_mail
from django.views.generic import DetailView
from django.urls import path
from django.urls import reverse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.html import format_html
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User, Group

from .models import Streamer, Staff, StaffPosition, SocialAccount, SMTPConfig, Message, ACLRule, RESOURCES, ACTIONS, Notification
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django import forms

# --------------------------------
# Admin Site personnalisé
# --------------------------------
from django.contrib.admin import AdminSite

class MyAdminSite(AdminSite):
    site_header = "Charity Streaming Admin"
    site_title = "Charity Streaming Admin Portal"
    index_title = "Bienvenue dans la console d'administration"

    index_template = "admin_custom/index.html"
    login_template = "admin_custom/login.html"
    logout_template = "admin_custom/logout.html"
    base_site_template = "admin_custom/base_site.html"

my_admin_site = MyAdminSite(name='myadmin')

# --------------------------------
# Admin pour SocialAccount (Inline)
# --------------------------------
class SocialAccountInline(admin.TabularInline):
    model = SocialAccount
    extra = 0  # pas de lignes vides par défaut
    fields = ("network", "username", "url",)
    readonly_fields = ("url",)

    # On peut auto-générer `url` dans `save()` du modèle, 
    # donc on le laisse en readonly

# --------------------------------
# Form pour Streamer (edition)
# --------------------------------
class StreamerForm(forms.ModelForm):
    class Meta:
        model = Streamer
        fields = [
            "twitch_name", "email", "description",
            "presence_mode", "discord",
            "broadcaster_type", "follower_count", "profile_image_url",
            "validated_by_admin"
        ]

# --------------------------------
# Admin pour Streamer
# --------------------------------
class StreamerAdmin(admin.ModelAdmin):
    form = StreamerForm
    inlines = [SocialAccountInline]

    # 1) Champ personnalisé qui renvoie un lien vers detail_view
    def twitch_name_link(self, obj):
        url = reverse("myadmin:streamer_detail", args=[obj.pk])
        return format_html("<a href='{}'>{}</a>", url, obj.twitch_name)
    twitch_name_link.short_description = "Twitch Name"

    # 2) Définir list_display pour afficher ce champ
    list_display = ("twitch_name_link", "email", "presence_mode", "validated_by_admin", "discord")
    list_filter = ('validated_by_admin',)
    search_fields = ('twitch_name', 'email')
    # 3) Indiquer que le lien se trouve sur twitch_name_link
    list_display_links = ("twitch_name_link",)

    # On peut supprimer (ou laisser) url_for_result : ce n’est souvent pas utilisé 
    # si on veut simplement que le lien soit sur le champ "twitch_name_link".
    # def url_for_result(self, result):
    #     pk = getattr(result, self.pk_attname)
    #     return reverse(f"{self.admin_site.name}:streamer_detail", args=[pk])

    change_form_template = "admin_custom/streamer_change_form.html"
    add_form_template = "admin_custom/streamer_change_form.html"

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path(
                "<path:object_id>/detail/",
                self.admin_site.admin_view(self.detail_view),
                name="streamer_detail",
            ),
            path(
                "<path:object_id>/validate_toggle/",
                self.admin_site.admin_view(self.validate_toggle),
                name="streamer_validate_toggle",
            )
        ]
        return my_urls + urls

    def detail_view(self, request, object_id):
        streamer = get_object_or_404(Streamer, pk=object_id)
        context = {
            "streamer": streamer,
            "opts": self.model._meta,
            "app_label": self.model._meta.app_label,
            "title": f"Profil du streamer {streamer.twitch_name}",
            "media": self.media,
            "admin_site": self.admin_site,
        }
        return render(request, "admin_custom/streamer_detail.html", context)

    def validate_toggle(self, request, object_id):
        streamer = get_object_or_404(Streamer, pk=object_id)
        streamer.validated_by_admin = not streamer.validated_by_admin
        streamer.save()
        messages.success(
            request,
            "L’inscription est maintenant " + ("validée" if streamer.validated_by_admin else "annulée")
        )
        return redirect(f"{self.admin_site.name}:streamer_detail", object_id=object_id)

    def response_change(self, request, obj):
        res = super().response_change(request, obj)
        if "_continue" not in request.POST and "_addanother" not in request.POST:
            return redirect(f"{self.admin_site.name}:streamer_detail", object_id=obj.pk)
        return res

@admin.register(Message, site=my_admin_site)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("subject", "from_user", "to_user", "timestamp", "read")
    list_filter = ("read", "timestamp")
    search_fields = ("subject", "body", "from_user__username", "to_user__username")
    ordering = ("-timestamp",)
    readonly_fields = ("timestamp",)

class GroupAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    filter_horizontal = ("permissions",)

admin.site.unregister(Group)  # On désenregistre d'abord la version par défaut
admin.site.register(Group, GroupAdmin)

# Permettre aussi la gestion des permissions spécifiques
class PermissionAdmin(admin.ModelAdmin):
    list_display = ("name", "codename", "content_type")
    list_filter = ("content_type",)
    search_fields = ("name", "codename")
# Désenregistrer le modèle Permission s'il est déjà enregistré
try:
    admin.site.unregister(Permission)
except admin.sites.NotRegistered:
    pass  # Si déjà non enregistré, on passe

admin.site.register(Permission, PermissionAdmin)

class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "is_staff", "is_active")
    actions = ["assign_streamer_role", "assign_staff_role"]

    @admin.action(description="Assigner le rôle de Streamer")
    def assign_streamer_role(self, request, queryset):
        streamer_group = Group.objects.get(name="Streamer")
        for user in queryset:
            user.groups.add(streamer_group)
        self.message_user(request, "Le rôle Streamer a été assigné avec succès.")

    @admin.action(description="Assigner le rôle de Staff")
    def assign_staff_role(self, request, queryset):
        staff_group = Group.objects.get(name="Staff")
        for user in queryset:
            user.groups.add(staff_group)
        self.message_user(request, "Le rôle Staff a été assigné avec succès.")

admin.site.unregister(User)  # Désenregistrer l'admin utilisateur par défaut
admin.site.register(User, UserAdmin)

# Admin pour ACLRule
class ACLRuleForm(forms.ModelForm):
    resource = forms.ChoiceField(choices=RESOURCES, label="Ressource")
    action = forms.ChoiceField(choices=ACTIONS, label="Action")

    class Meta:
        model = ACLRule
        fields = ['group', 'user', 'resource', 'action']

class ACLRuleAdmin(admin.ModelAdmin):
    form = ACLRuleForm
    list_display = ('group', 'user', 'resource', 'action')  # Champs à afficher dans la liste
    list_filter = ('resource', 'action')  # Ajoute des filtres sur les colonnes
    search_fields = ('group__name', 'user__username', 'resource', 'action')  # Champs pour la recherche

# Enregistrez correctement ACLRule dans my_admin_site
my_admin_site.register(ACLRule, ACLRuleAdmin)

class StreamerDetailView(DetailView):
    model = Streamer
    template_name = 'admin_custom/streamer_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'is_popup': False,
            'is_nav_sidebar_enabled': True,
            'subtitle': f"Profil du streamer {self.object.name}",
            'admin_site': site,  # Assurez-vous que l'objet `admin_site` est accessible
        })
        return context

@staticmethod
def validate_streamer(request, streamer_id):
    logger.debug("Méthode validate_streamer appelée.")
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

    logger.debug("Email envoyé à %s", streamer.email)
    messages.success(request, 'Le streamer a été validé et un email a été envoyé.')
    return redirect('admin_dashboard')

@admin.action(description="Valider le streamer et envoyer un email")
def validate_selected_streamers(modeladmin, request, queryset):
    for streamer in queryset:
        streamer.validated_by_admin = True
        streamer.save()

        # Envoi de l'email
        if streamer.email:
            send_mail(
                'Bienvenue à notre événement',
                f'Bonjour {streamer.twitch_name}, votre inscription est validée.',
                'test@forestt.run',
                [streamer.email],
                fail_silently=False,
            )
            messages.success(request, f"L'email a été envoyé à {streamer.email}.")
        else:
            messages.warning(request, f"Aucun email défini pour le streamer {streamer.twitch_name}.")

class StreamerAdmin(admin.ModelAdmin):
    list_display = ('twitch_name', 'validated_by_admin', 'email', 'created_at')
    actions = [validate_selected_streamers]

class NotificationForm(forms.ModelForm):
    class Meta:
        model = Notification
        fields = ['title', 'message', 'type', 'recipient_user', 'recipient_group']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Permet d'avoir un choix "Aucun" pour les utilisateurs et les groupes
        self.fields['recipient_user'].required = False
        self.fields['recipient_user'].widget.attrs['class'] = 'vTextField'

        self.fields['recipient_group'].required = False
        self.fields['recipient_group'].widget.attrs['class'] = 'vTextField'

    def clean(self):
        cleaned_data = super().clean()
        user = cleaned_data.get("recipient_user")
        group = cleaned_data.get("recipient_group")

        if not user and not group:
            raise forms.ValidationError("Vous devez sélectionner au moins un utilisateur ou un groupe.")

        return cleaned_data

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    form = NotificationForm  # Utilisation du formulaire personnalisé
    list_display = ('title', 'type', 'recipient_user', 'recipient_group', 'created_at', 'is_read')
    list_filter = ('type', 'is_read', 'created_at')
    search_fields = ('title', 'message', 'recipient_user__username', 'recipient_group__name')
    actions = ['mark_as_read']

    def has_add_permission(self, request):
        """ Permet d'afficher le bouton d'ajout dans l'admin """
        return True  # ✅ Vérifie que l'ajout est autorisé

    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
        self.message_user(request, "Les notifications sélectionnées ont été marquées comme lues.")

    mark_as_read.short_description = "Marquer comme lues"

# --------------------------------
# On enregistre tout ça
# --------------------------------

my_admin_site.register(Staff)
my_admin_site.register(StaffPosition)
my_admin_site.register(SocialAccount)
my_admin_site.register(Streamer, StreamerAdmin)
my_admin_site.register(SMTPConfig)
my_admin_site.register(Notification, NotificationAdmin)