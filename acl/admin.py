from django.contrib import admin
from .models import ACLRule

class ACLRuleAdmin(admin.ModelAdmin):
    list_display = ('group', 'user', 'resource', 'action')
    list_filter = ('resource', 'action')
    search_fields = ('group__name', 'user__username', 'resource', 'action')

admin.site.register(ACLRule, ACLRuleAdmin)
