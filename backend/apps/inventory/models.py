"""
ISP Software - Inventory Models

Note: Reseller and HR/Staff models are intentionally NOT defined here.
They live in their dedicated apps `apps.reseller` and `apps.hr`.
Defining them in multiple apps creates duplicate database tables.
"""
from django.db import models
from django.conf import settings
import uuid


# ─────────────────────────────────────────
# INVENTORY
# ─────────────────────────────────────────

class ProductCategory(models.Model):
    name        = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    """Hardware/equipment catalog"""
    UNIT_CHOICES = [('pcs', 'Pieces'), ('meter', 'Meter'), ('roll', 'Roll'), ('box', 'Box')]

    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category    = models.ForeignKey(ProductCategory, on_delete=models.SET_NULL, null=True)
    name        = models.CharField(max_length=200)
    code        = models.CharField(max_length=50, unique=True)
    brand       = models.CharField(max_length=100, blank=True)
    model       = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    unit        = models.CharField(max_length=20, choices=UNIT_CHOICES, default='pcs')
    unit_cost   = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    stock_quantity  = models.IntegerField(default=0)
    min_stock   = models.IntegerField(default=5, help_text='Alert when stock below this')
    warranty_months = models.PositiveIntegerField(default=0)
    has_serial  = models.BooleanField(default=False)
    barcode     = models.CharField(max_length=100, blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.code})"

    @property
    def is_low_stock(self):
        return self.stock_quantity <= self.min_stock


class StockMovement(models.Model):
    """Stock in/out records"""
    TYPE_CHOICES = [
        ('purchase',    'Purchase'),
        ('issue',       'Issued to Technician'),
        ('return',      'Returned'),
        ('assigned',    'Assigned to Customer'),
        ('retrieved',   'Retrieved from Customer'),
        ('damaged',     'Damaged/Written Off'),
        ('adjustment',  'Stock Adjustment'),
    ]
    product     = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='movements')
    type        = models.CharField(max_length=20, choices=TYPE_CHOICES)
    quantity    = models.IntegerField()
    unit_cost   = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    reference   = models.CharField(max_length=100, blank=True)
    notes       = models.TextField(blank=True)
    performed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at  = models.DateTimeField(auto_now_add=True)


class CustomerEquipment(models.Model):
    """Equipment assigned to customers"""
    customer    = models.ForeignKey('customers.Customer', on_delete=models.CASCADE,
                                    related_name='equipment')
    product     = models.ForeignKey(Product, on_delete=models.PROTECT)
    serial_number = models.CharField(max_length=100, blank=True)
    assigned_at = models.DateTimeField(auto_now_add=True)
    is_returned = models.BooleanField(default=False)
    returned_at = models.DateTimeField(null=True, blank=True)
    condition   = models.CharField(max_length=50, blank=True)
    is_owned_by_customer = models.BooleanField(default=False)
