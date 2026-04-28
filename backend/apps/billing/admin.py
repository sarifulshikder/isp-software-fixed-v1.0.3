from django.contrib import admin
from .models import Invoice, InvoiceItem, CreditNote, Discount


class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 0
    readonly_fields = ['total']


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display  = ['invoice_number', 'customer', 'invoice_type', 'total',
                     'amount_paid', 'balance_due', 'status', 'due_date']
    list_filter   = ['status', 'invoice_type']
    search_fields = ['invoice_number', 'customer__first_name', 'customer__customer_id']
    readonly_fields = ['invoice_number', 'created_at', 'updated_at']
    inlines = [InvoiceItemInline]


@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'type', 'value', 'uses_count', 'is_active', 'valid_until']
    list_filter  = ['type', 'is_active']

admin.site.register(CreditNote)
