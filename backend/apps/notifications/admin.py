from django.contrib import admin
from .models import NotificationTemplate, NotificationLog

@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'event', 'channel', 'is_active']
    list_filter  = ['channel', 'is_active']

@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display  = ['recipient', 'channel', 'status', 'sent_at']
    list_filter   = ['channel', 'status']
    search_fields = ['recipient']
    readonly_fields = ['sent_at']
