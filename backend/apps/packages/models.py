"""
ISP Software - Package & Plan Models
"""
from django.db import models
import uuid


class Package(models.Model):
    """Internet service packages"""

    BILLING_CYCLE = [
        ('hourly',   'Hourly'),
        ('daily',    'Daily'),
        ('weekly',   'Weekly'),
        ('monthly',  'Monthly'),
        ('quarterly','Quarterly'),
        ('yearly',   'Yearly'),
    ]

    BANDWIDTH_TYPE = [
        ('shared',    'Shared'),
        ('dedicated', 'Dedicated'),
    ]

    id              = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name            = models.CharField(max_length=100)
    code            = models.CharField(max_length=20, unique=True)
    description     = models.TextField(blank=True)

    # Speed
    download_speed  = models.PositiveIntegerField(help_text='Speed in Kbps')
    upload_speed    = models.PositiveIntegerField(help_text='Speed in Kbps')
    bandwidth_type  = models.CharField(max_length=20, choices=BANDWIDTH_TYPE, default='shared')
    contention_ratio = models.PositiveIntegerField(default=1, help_text='e.g. 1:8')

    # Data
    data_limit      = models.BigIntegerField(null=True, blank=True, help_text='Data cap in MB, null=unlimited')
    fup_speed       = models.PositiveIntegerField(null=True, blank=True, help_text='Speed after FUP in Kbps')
    fup_threshold   = models.BigIntegerField(null=True, blank=True, help_text='FUP trigger in MB')

    # Pricing
    price           = models.DecimalField(max_digits=10, decimal_places=2)
    billing_cycle   = models.CharField(max_length=20, choices=BILLING_CYCLE, default='monthly')
    setup_fee       = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_inclusive   = models.BooleanField(default=True)

    # Services included
    includes_tv     = models.BooleanField(default=False)
    includes_phone  = models.BooleanField(default=False)
    ip_addresses    = models.PositiveIntegerField(default=1)

    # Status
    is_active       = models.BooleanField(default=True)
    is_public       = models.BooleanField(default=True, help_text='Visible to customers')
    sort_order      = models.PositiveIntegerField(default=0)

    # Mikrotik
    mikrotik_profile = models.CharField(max_length=100, blank=True)
    radius_group     = models.CharField(max_length=100, blank=True)

    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['sort_order', 'price']

    def __str__(self):
        return f"{self.name} ({self.get_speed_display()})"

    def get_speed_display(self):
        def fmt(kbps):
            if kbps >= 1000000:
                return f"{kbps/1000000:.0f}G"
            elif kbps >= 1000:
                return f"{kbps/1000:.0f}M"
            return f"{kbps}K"
        return f"{fmt(self.download_speed)}/{fmt(self.upload_speed)}"


class PackagePriceHistory(models.Model):
    """Track price changes for packages"""
    package     = models.ForeignKey(Package, on_delete=models.CASCADE, related_name='price_history')
    old_price   = models.DecimalField(max_digits=10, decimal_places=2)
    new_price   = models.DecimalField(max_digits=10, decimal_places=2)
    changed_by  = models.CharField(max_length=200)
    reason      = models.TextField(blank=True)
    changed_at  = models.DateTimeField(auto_now_add=True)
