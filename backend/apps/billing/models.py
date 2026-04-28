"""
ISP Software - Billing & Invoice Models
"""
from django.db import models
from django.conf import settings
import uuid


class Invoice(models.Model):
    """Customer invoices"""

    STATUS_CHOICES = [
        ('draft',       'Draft'),
        ('pending',     'Pending'),
        ('partial',     'Partially Paid'),
        ('paid',        'Paid'),
        ('overdue',     'Overdue'),
        ('cancelled',   'Cancelled'),
        ('waived',      'Waived'),
    ]

    TYPE_CHOICES = [
        ('monthly',      'Monthly Bill'),
        ('installation', 'Installation Fee'),
        ('reconnection', 'Reconnection Fee'),
        ('upgrade',      'Package Upgrade'),
        ('misc',         'Miscellaneous'),
    ]

    id              = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    invoice_number  = models.CharField(max_length=30, unique=True, editable=False)
    customer        = models.ForeignKey('customers.Customer', on_delete=models.PROTECT,
                                        related_name='invoices')
    invoice_type    = models.CharField(max_length=20, choices=TYPE_CHOICES, default='monthly')
    status          = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # Amounts
    subtotal        = models.DecimalField(max_digits=10, decimal_places=2)
    discount        = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_amount      = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    late_fee        = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total           = models.DecimalField(max_digits=10, decimal_places=2)
    amount_paid     = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    balance_due     = models.DecimalField(max_digits=10, decimal_places=2)

    # Dates
    billing_period_start = models.DateField()
    billing_period_end   = models.DateField()
    due_date        = models.DateField()
    paid_date       = models.DateField(null=True, blank=True)

    # Package snapshot at time of billing
    package_name    = models.CharField(max_length=100)
    package_price   = models.DecimalField(max_digits=10, decimal_places=2)

    # Notes
    notes           = models.TextField(blank=True)
    internal_notes  = models.TextField(blank=True)

    # Metadata
    created_by      = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                        null=True, related_name='created_invoices')
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['customer', 'status']),
            models.Index(fields=['invoice_number']),
            models.Index(fields=['due_date']),
        ]

    def __str__(self):
        return f"{self.invoice_number} - {self.customer} - {self.total}"

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            from django.utils import timezone
            year_month = timezone.now().strftime('%Y%m')
            last = Invoice.objects.filter(
                invoice_number__startswith=f'INV-{year_month}'
            ).order_by('-invoice_number').first()
            num = int(last.invoice_number[-5:]) + 1 if last else 1
            self.invoice_number = f"INV-{year_month}-{num:05d}"
        self.balance_due = self.total - self.amount_paid
        super().save(*args, **kwargs)

    @property
    def is_overdue(self):
        from django.utils import timezone
        return self.status == 'pending' and self.due_date < timezone.now().date()


class InvoiceItem(models.Model):
    """Line items for invoices"""
    invoice     = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    description = models.CharField(max_length=255)
    quantity    = models.DecimalField(max_digits=8, decimal_places=2, default=1)
    unit_price  = models.DecimalField(max_digits=10, decimal_places=2)
    total       = models.DecimalField(max_digits=10, decimal_places=2)


class CreditNote(models.Model):
    """Credit notes for refunds/adjustments"""
    invoice     = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='credit_notes')
    customer    = models.ForeignKey('customers.Customer', on_delete=models.CASCADE)
    amount      = models.DecimalField(max_digits=10, decimal_places=2)
    reason      = models.TextField()
    created_by  = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at  = models.DateTimeField(auto_now_add=True)


class Discount(models.Model):
    """Discount codes and rules"""
    TYPE_CHOICES = [
        ('percentage', 'Percentage'),
        ('fixed',      'Fixed Amount'),
    ]
    name        = models.CharField(max_length=100)
    code        = models.CharField(max_length=20, unique=True)
    type        = models.CharField(max_length=20, choices=TYPE_CHOICES)
    value       = models.DecimalField(max_digits=10, decimal_places=2)
    max_uses    = models.PositiveIntegerField(null=True, blank=True)
    uses_count  = models.PositiveIntegerField(default=0)
    valid_from  = models.DateField()
    valid_until = models.DateField(null=True, blank=True)
    is_active   = models.BooleanField(default=True)
    applicable_packages = models.ManyToManyField('packages.Package', blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)
