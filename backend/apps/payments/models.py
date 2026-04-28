"""
ISP Software - Payment Models
"""
from django.db import models
from django.conf import settings
import uuid


class Payment(models.Model):
    """Customer payment records"""

    METHOD_CHOICES = [
        ('cash',        'Cash'),
        ('bank',        'Bank Transfer'),
        ('bkash',       'bKash'),
        ('nagad',       'Nagad'),
        ('rocket',      'Rocket'),
        ('card',        'Credit/Debit Card'),
        ('stripe',      'Stripe'),
        ('cheque',      'Cheque'),
        ('advance',     'Advance Balance'),
        ('other',       'Other'),
    ]

    STATUS_CHOICES = [
        ('pending',     'Pending'),
        ('completed',   'Completed'),
        ('failed',      'Failed'),
        ('refunded',    'Refunded'),
        ('disputed',    'Disputed'),
    ]

    id              = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    payment_number  = models.CharField(max_length=30, unique=True, editable=False)
    customer        = models.ForeignKey('customers.Customer', on_delete=models.PROTECT,
                                        related_name='payments')
    invoice         = models.ForeignKey('billing.Invoice', on_delete=models.SET_NULL,
                                        null=True, blank=True, related_name='payments')
    method          = models.CharField(max_length=20, choices=METHOD_CHOICES)
    status          = models.CharField(max_length=20, choices=STATUS_CHOICES, default='completed')

    amount          = models.DecimalField(max_digits=10, decimal_places=2)
    currency        = models.CharField(max_length=3, default='BDT')

    # Transaction details
    transaction_id  = models.CharField(max_length=100, blank=True)
    reference       = models.CharField(max_length=100, blank=True)
    gateway_response = models.JSONField(null=True, blank=True)

    # Collection
    collected_by    = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                        null=True, blank=True, related_name='collected_payments')
    collection_area = models.CharField(max_length=100, blank=True)

    notes           = models.TextField(blank=True)
    payment_date    = models.DateTimeField()
    created_at      = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-payment_date']
        indexes = [
            models.Index(fields=['customer', 'status']),
            models.Index(fields=['payment_date']),
            models.Index(fields=['method']),
        ]

    def __str__(self):
        return f"{self.payment_number} - {self.customer} - {self.amount}"

    def save(self, *args, **kwargs):
        if not self.payment_number:
            from django.utils import timezone
            ts = timezone.now().strftime('%Y%m%d%H%M%S')
            import random
            self.payment_number = f"PAY-{ts}-{random.randint(100,999)}"
        super().save(*args, **kwargs)


class Refund(models.Model):
    """Refund records"""
    payment     = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='refunds')
    amount      = models.DecimalField(max_digits=10, decimal_places=2)
    reason      = models.TextField()
    processed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    processed_at = models.DateTimeField(auto_now_add=True)


class PaymentGatewayConfig(models.Model):
    """Configuration for payment gateways"""
    name        = models.CharField(max_length=50, unique=True)
    is_active   = models.BooleanField(default=False)
    config      = models.JSONField(default=dict)  # Encrypted credentials
    updated_at  = models.DateTimeField(auto_now=True)
