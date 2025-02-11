from django.contrib import admin
from django.contrib.auth.models import Group, User
from .models import Streamer, Staff, Tag, UserProfile,  BlacklistedStreamer, StaffPosition, StaffApplication

class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

admin.site.register(Tag, TagAdmin)

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user',)
    filter_horizontal = ('tags',)

admin.site.register(UserProfile, UserProfileAdmin)

class StreamerAdmin(admin.ModelAdmin):
    list_display = ('twitch_name', 'email', 'validated_by_admin', 'created_at')
    list_filter = ('validated_by_admin',)
    search_fields = ('twitch_name', 'email')

admin.site.register(Streamer, StreamerAdmin)

class BlacklistedStreamerAdmin(admin.ModelAdmin):
    list_display = ('twitch_name',)
    search_fields = ('twitch_name',)

admin.site.register(BlacklistedStreamer, BlacklistedStreamerAdmin)

class StaffPositionAdmin(admin.ModelAdmin):
    list_display = ('poste', 'mode', 'nombre_de_postes')
    list_filter = ('mode',)
    search_fields = ('poste',)

admin.site.register(StaffPosition, StaffPositionAdmin)

class StaffApplicationAdmin(admin.ModelAdmin):
    list_display = ('pseudo', 'poste_demande', 'status', 'created_at', 'postes_disponibles', 'nombre_reserve', 'get_tags_display')
    list_filter = ('status', 'poste_demande')
    search_fields = ('pseudo', 'email')
    readonly_fields = ('get_tags_display',)
    
    # Vous pouvez ajouter ici des actions personnalisées si besoin
admin.site.register(StaffApplication, StaffApplicationAdmin)
