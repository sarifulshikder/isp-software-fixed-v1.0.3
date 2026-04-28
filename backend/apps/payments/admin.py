from django.contrib import admin
from .models import Payment, Refund, PaymentGatewayConfig


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display  = ['payment_number', 'customer', 'method', 'amount', 'status',
                     'collected_by', 'payment_date']
    list_filter   = ['method', 'status']
    search_fields = ['payment_number', 'customer__first_name', 'customer__customer_id', 'transaction_id']
    readonly_fields = ['payment_number', 'created_at']


@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    list_display = ['payment', 'amount', 'processed_by', 'processed_at']


@admin.register(PaymentGatewayConfig)
class PaymentGatewayConfigAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'updated_at']
