from django.contrib import admin
from .models import Notification

class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'type', 'recipient_user', 'recipient_group', 'recipient_tag', 'created_at', 'is_read')
    list_filter = ('type', 'is_read', 'created_at')
    search_fields = ('title', 'message')
    
admin.site.register(Notification, NotificationAdmin)
