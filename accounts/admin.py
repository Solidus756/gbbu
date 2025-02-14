from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from import_export.admin import ImportExportModelAdmin
from django.contrib.auth.models import Group, User
from .models import Streamer, Staff, Tag, UserProfile,  BlacklistedStreamer, StaffPosition, StaffApplication, SMTPConfig
from django_form_builder.models import FormEntry


admin.site.register(SMTPConfig)

class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

admin.site.register(Tag, TagAdmin)

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user',)
    filter_horizontal = ('tags',)

admin.site.register(UserProfile, UserProfileAdmin)
'''
class StreamerAdmin(admin.ModelAdmin):
    list_display = ('twitch_name', 'email', 'validated_by_admin', 'created_at')
    list_filter = ('validated_by_admin',)
    search_fields = ('twitch_name', 'email')

admin.site.register(Streamer, StreamerAdmin)
'''
class BlacklistedStreamerAdmin(admin.ModelAdmin):
    list_display = ('twitch_name',)
    search_fields = ('twitch_name',)

admin.site.register(BlacklistedStreamer, BlacklistedStreamerAdmin)

class StaffPositionAdmin(admin.ModelAdmin):
    list_display = ('poste', 'mode', 'nombre_de_postes')
    list_filter = ('mode',)
    search_fields = ('poste',)

admin.site.register(StaffPosition, StaffPositionAdmin)

class StaffApplicationInline(admin.StackedInline):
    model = StaffApplication
    extra = 0
    readonly_fields = ('pseudo', 'pseudo_discord', 'pseudo_twitch', 'email', 'poste_demande', 'pourquoi', 'status')
    can_delete = False

@admin.register(Streamer)
class StreamerAdmin(admin.ModelAdmin):
    list_display = ('twitch_name', 'email', 'validated_by_admin')
    inlines = [StaffApplicationInline]
    
    def get_readonly_fields(self, request, obj=None):
        # Retourner tous les champs en lecture seule (si c'est votre choix pour la vue par défaut)
        return [f.name for f in self.model._meta.fields]
    
    def change_view(self, request, object_id, form_url='', extra_context=None):
        if extra_context is None:
            extra_context = {}
        extra_context['title'] = "Aperçu du profil (Lecture seule)"
        return super().change_view(request, object_id, form_url, extra_context=extra_context)

class FormEntryResource(resources.ModelResource):
    class Meta:
        model = FormEntry
        # Vous pouvez préciser les champs ou exclure certains si nécessaire

@admin.register(FormEntry)
class FormEntryAdmin(ImportExportModelAdmin):
    resource_class = FormEntryResource
    list_display = ('form', 'submitted_at', 'user')  # Adaptez selon votre modèle
