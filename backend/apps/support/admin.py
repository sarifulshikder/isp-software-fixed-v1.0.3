from django.contrib import admin
from .models import Ticket, TicketComment, FieldVisit, KnowledgeBase


class TicketCommentInline(admin.TabularInline):
    model = TicketComment
    extra = 0
    readonly_fields = ['created_at']


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display  = ['ticket_number', 'customer', 'subject', 'category',
                     'priority', 'status', 'assigned_to', 'sla_breached', 'created_at']
    list_filter   = ['status', 'priority', 'category', 'sla_breached']
    search_fields = ['ticket_number', 'subject', 'customer__first_name']
    readonly_fields = ['ticket_number', 'created_at', 'updated_at']
    inlines       = [TicketCommentInline]


@admin.register(KnowledgeBase)
class KnowledgeBaseAdmin(admin.ModelAdmin):
    list_display  = ['title', 'category', 'is_public', 'views', 'created_at']
    list_filter   = ['category', 'is_public']
    search_fields = ['title']
    prepopulated_fields = {'slug': ('title',)}

admin.site.register(FieldVisit)
admin.site.register(TicketComment)
