from django.contrib import admin
from .models import Package, PackagePriceHistory


@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    list_display  = ['code', 'name', 'get_speed_display', 'price',
                     'billing_cycle', 'bandwidth_type', 'is_active', 'is_public']
    list_filter   = ['billing_cycle', 'bandwidth_type', 'is_active', 'is_public']
    search_fields = ['name', 'code']
    readonly_fields = ['created_at', 'updated_at']

admin.site.register(PackagePriceHistory)
