from django.contrib import admin
from .models import Reseller, ResellerCommission

@admin.register(Reseller)
class ResellerAdmin(admin.ModelAdmin):
    list_display  = ['company_name', 'contact_person', 'phone', 'commission_rate', 'balance', 'is_active']
    list_filter   = ['is_active']
    search_fields = ['company_name', 'contact_person', 'phone']

@admin.register(ResellerCommission)
class ResellerCommissionAdmin(admin.ModelAdmin):
    list_display = ['reseller', 'amount', 'is_paid', 'created_at']
    list_filter  = ['is_paid']
