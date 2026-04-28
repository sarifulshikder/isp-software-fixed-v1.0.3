"""
ISP Software - Customer Management Models
"""
from django.db import models, transaction
from django.conf import settings
import uuid


class Zone(models.Model):
    """Geographic zones/areas for customers"""
    name        = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active   = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Customer(models.Model):
    """Main customer model"""

    STATUS_CHOICES = [
        ('active',      'Active'),
        ('inactive',    'Inactive'),
        ('suspended',   'Suspended'),
        ('terminated',  'Terminated'),
        ('pending',     'Pending Activation'),
    ]

    CONNECTION_TYPE = [
        ('fiber',   'Fiber (FTTH)'),
        ('cable',   'Cable'),
        ('wireless','Wireless'),
        ('dsl',     'DSL'),
        ('wimax',   'WiMAX'),
    ]

    id              = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer_id     = models.CharField(max_length=20, unique=True, editable=False)
    user            = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                           related_name='customer_profile', null=True, blank=True)
    # Personal Info
    first_name      = models.CharField(max_length=100)
    last_name       = models.CharField(max_length=100)
    email           = models.EmailField(blank=True)
    phone           = models.CharField(max_length=20)
    alt_phone       = models.CharField(max_length=20, blank=True)
    nid_number      = models.CharField(max_length=20, blank=True)
    nid_document    = models.FileField(upload_to='kyc/nid/', blank=True, null=True)
    photo           = models.ImageField(upload_to='customers/photos/', blank=True, null=True)
    date_of_birth   = models.DateField(null=True, blank=True)

    # Address
    address         = models.TextField()
    area            = models.CharField(max_length=100)
    city            = models.CharField(max_length=100)
    zone            = models.ForeignKey(Zone, on_delete=models.SET_NULL, null=True)
    latitude        = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude       = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    # Connection
    connection_type = models.CharField(max_length=20, choices=CONNECTION_TYPE, default='fiber')
    package         = models.ForeignKey('packages.Package', on_delete=models.PROTECT,
                                        related_name='customers')
    reseller        = models.ForeignKey('reseller.Reseller', on_delete=models.SET_NULL,
                                        null=True, blank=True, related_name='customers')
    assigned_agent  = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                        null=True, blank=True, related_name='managed_customers')

    # Network
    ip_address      = models.GenericIPAddressField(null=True, blank=True)
    mac_address     = models.CharField(max_length=17, blank=True)
    pppoe_username  = models.CharField(max_length=100, blank=True)
    pppoe_password  = models.CharField(max_length=100, blank=True)
    vlan_id         = models.PositiveIntegerField(null=True, blank=True)
    onu_serial      = models.CharField(max_length=50, blank=True)
    olt_port        = models.CharField(max_length=50, blank=True)

    # Billing
    status          = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    billing_day     = models.PositiveIntegerField(default=1)
    advance_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    credit_limit    = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    installation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    installation_paid = models.BooleanField(default=False)

    # Dates
    connection_date = models.DateField(null=True, blank=True)
    expiry_date     = models.DateField(null=True, blank=True)
    suspension_date = models.DateField(null=True, blank=True)
    termination_date = models.DateField(null=True, blank=True)

    # Metadata
    notes           = models.TextField(blank=True)
    tags            = models.JSONField(default=list, blank=True)
    created_by      = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                        null=True, related_name='created_customers')
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['customer_id']),
            models.Index(fields=['phone']),
            models.Index(fields=['status']),
            models.Index(fields=['zone']),
        ]

    def __str__(self):
        return f"{self.customer_id} - {self.first_name} {self.last_name}"

    def save(self, *args, **kwargs):
        if not self.customer_id:
            with transaction.atomic():
                last = (
                    Customer.objects
                    .select_for_update()
                    .order_by('-customer_id')
                    .first()
                )
                num = int(last.customer_id[3:]) + 1 if last and last.customer_id else 1
                self.customer_id = f"ISP{num:06d}"
                super().save(*args, **kwargs)
            return
        super().save(*args, **kwargs)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def is_expired(self):
        from django.utils import timezone
        if self.expiry_date:
            return self.expiry_date < timezone.now().date()
        return False


class CustomerDocument(models.Model):
    """KYC and other documents for customers"""
    DOC_TYPES = [
        ('nid',         'National ID'),
        ('passport',    'Passport'),
        ('driving',     'Driving License'),
        ('contract',    'Service Contract'),
        ('other',       'Other'),
    ]
    customer    = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='documents')
    doc_type    = models.CharField(max_length=20, choices=DOC_TYPES)
    title       = models.CharField(max_length=200)
    file        = models.FileField(upload_to='customers/documents/')
    is_verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                    null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)


class CustomerNote(models.Model):
    """Internal notes on customers"""
    customer    = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='customer_notes')
    author      = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    note        = models.TextField()
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
