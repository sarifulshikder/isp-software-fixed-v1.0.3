"""
ISP Software - Custom User & Authentication Models
"""
from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid


class User(AbstractUser):
    """Extended user model with ISP-specific fields"""

    ROLE_CHOICES = [
        ('superadmin',  'Super Admin'),
        ('admin',       'Admin'),
        ('manager',     'Manager'),
        ('accountant',  'Accountant'),
        ('technician',  'Technician'),
        ('agent',       'Collection Agent'),
        ('support',     'Support Staff'),
        ('reseller',    'Reseller'),
        ('customer',    'Customer'),
    ]

    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email       = models.EmailField(unique=True)
    role        = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    phone       = models.CharField(max_length=20, blank=True)
    avatar      = models.ImageField(upload_to='avatars/', blank=True, null=True)
    is_2fa_enabled = models.BooleanField(default=False)
    last_login_ip  = models.GenericIPAddressField(null=True, blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_full_name()} ({self.role})"

    @property
    def full_name(self):
        return self.get_full_name()

    def has_role(self, *roles):
        return self.role in roles


class Permission(models.Model):
    """Granular permissions for ISP staff"""
    user        = models.ForeignKey(User, on_delete=models.CASCADE, related_name='custom_permissions')
    module      = models.CharField(max_length=50)
    can_view    = models.BooleanField(default=True)
    can_create  = models.BooleanField(default=False)
    can_edit    = models.BooleanField(default=False)
    can_delete  = models.BooleanField(default=False)
    can_export  = models.BooleanField(default=False)

    class Meta:
        unique_together = ['user', 'module']

    def __str__(self):
        return f"{self.user.email} - {self.module}"
