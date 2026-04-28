from django.contrib import admin
from .models import Customer, Zone, CustomerDocument, CustomerNote

@admin.register(Zone)
class ZoneAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'created_at']

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display  = ['customer_id', 'first_name', 'last_name', 'phone', 'status', 'package', 'zone', 'expiry_date']
    list_filter   = ['status', 'zone', 'package', 'connection_type']
    search_fields = ['customer_id', 'first_name', 'last_name', 'phone', 'pppoe_username']
    readonly_fields = ['customer_id', 'created_at', 'updated_at']

@admin.register(CustomerDocument)
class CustomerDocumentAdmin(admin.ModelAdmin):
    list_display = ['customer', 'doc_type', 'is_verified', 'uploaded_at']

admin.site.register(CustomerNote)
