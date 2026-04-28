from django.contrib import admin
from .models import ReportTemplate

@admin.register(ReportTemplate)
class ReportTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'report_type', 'created_by', 'is_shared', 'created_at']
    list_filter  = ['report_type', 'is_shared']
