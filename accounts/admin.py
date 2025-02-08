from django.contrib import admin
from django.contrib.auth.models import Group, User
from .models import Streamer, Staff, Tag, UserProfile

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

class StaffAdmin(admin.ModelAdmin):
    list_display = ('user', 'first_name', 'last_name', 'email')
    search_fields = ('first_name', 'last_name', 'email')

admin.site.register(Staff, StaffAdmin)
