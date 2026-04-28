import uuid
from django.db import models
from django.conf import settings


class Reseller(models.Model):
    id             = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user           = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reseller_profile')
    company_name   = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=100)
    phone          = models.CharField(max_length=20)
    email          = models.EmailField()
    address        = models.TextField()
    commission_rate= models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text='Commission %')
    bandwidth_pool = models.PositiveIntegerField(default=0, help_text='Allocated Mbps')
    credit_limit   = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    balance        = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active      = models.BooleanField(default=True)
    parent         = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='sub_resellers')
    created_at     = models.DateTimeField(auto_now_add=True)
    updated_at     = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.company_name

    @property
    def total_customers(self):
        from apps.customers.models import Customer
        return Customer.objects.filter(reseller=self).count()

    @property
    def active_customers(self):
        from apps.customers.models import Customer
        return Customer.objects.filter(reseller=self, status='active').count()


class ResellerCommission(models.Model):
    reseller   = models.ForeignKey(Reseller, on_delete=models.CASCADE, related_name='commissions')
    amount     = models.DecimalField(max_digits=10, decimal_places=2)
    reference  = models.CharField(max_length=100, blank=True)
    notes      = models.TextField(blank=True)
    is_paid    = models.BooleanField(default=False)
    paid_at    = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.reseller} - {self.amount}"
