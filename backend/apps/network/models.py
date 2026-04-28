"""
ISP Software - Network Management Models
"""
from django.db import models
from django.conf import settings
import uuid


class IPPool(models.Model):
    """IP address pools"""
    name        = models.CharField(max_length=100)
    network     = models.CharField(max_length=50, help_text='e.g. 192.168.1.0/24')
    gateway     = models.GenericIPAddressField()
    dns1        = models.GenericIPAddressField(default='8.8.8.8')
    dns2        = models.GenericIPAddressField(default='8.8.4.4')
    vlan_id     = models.PositiveIntegerField(null=True, blank=True)
    is_active   = models.BooleanField(default=True)
    description = models.TextField(blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.network})"


class IPAddress(models.Model):
    """Individual IP addresses"""
    STATUS_CHOICES = [
        ('available',  'Available'),
        ('assigned',   'Assigned'),
        ('reserved',   'Reserved'),
        ('blocked',    'Blocked'),
    ]

    pool        = models.ForeignKey(IPPool, on_delete=models.CASCADE, related_name='addresses')
    address     = models.GenericIPAddressField(unique=True)
    status      = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    customer    = models.ForeignKey('customers.Customer', on_delete=models.SET_NULL,
                                    null=True, blank=True, related_name='ip_addresses')
    assigned_at = models.DateTimeField(null=True, blank=True)
    notes       = models.TextField(blank=True)

    class Meta:
        ordering = ['address']

    def __str__(self):
        return f"{self.address} ({self.status})"


class NetworkDevice(models.Model):
    """Network equipment - routers, switches, OLTs"""

    DEVICE_TYPES = [
        ('router',   'Router'),
        ('switch',   'Switch'),
        ('olt',      'OLT (Fiber)'),
        ('onu',      'ONU/ONT'),
        ('ap',       'Access Point'),
        ('splitter', 'Fiber Splitter'),
        ('server',   'Server'),
        ('other',    'Other'),
    ]

    STATUS_CHOICES = [
        ('online',   'Online'),
        ('offline',  'Offline'),
        ('warning',  'Warning'),
        ('unknown',  'Unknown'),
    ]

    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name        = models.CharField(max_length=100)
    device_type = models.CharField(max_length=20, choices=DEVICE_TYPES)
    brand       = models.CharField(max_length=50, blank=True)
    model       = models.CharField(max_length=100, blank=True)
    serial      = models.CharField(max_length=100, blank=True)
    ip_address  = models.GenericIPAddressField(null=True, blank=True)
    mac_address = models.CharField(max_length=17, blank=True)
    location    = models.CharField(max_length=200, blank=True)
    status      = models.CharField(max_length=20, choices=STATUS_CHOICES, default='unknown')
    snmp_community = models.CharField(max_length=100, default='public')
    ssh_username = models.CharField(max_length=100, blank=True)
    ssh_password = models.CharField(max_length=100, blank=True)
    api_port    = models.PositiveIntegerField(default=8728)  # Mikrotik API port
    uptime      = models.CharField(max_length=50, blank=True)
    firmware    = models.CharField(max_length=50, blank=True)
    customer    = models.ForeignKey('customers.Customer', on_delete=models.SET_NULL,
                                    null=True, blank=True, related_name='network_devices')
    notes       = models.TextField(blank=True)
    last_seen   = models.DateTimeField(null=True, blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.device_type}) - {self.ip_address}"


class RADIUSSession(models.Model):
    """Active RADIUS sessions"""
    customer        = models.ForeignKey('customers.Customer', on_delete=models.CASCADE,
                                        related_name='radius_sessions')
    username        = models.CharField(max_length=100)
    session_id      = models.CharField(max_length=100, unique=True)
    nas_ip          = models.GenericIPAddressField()
    framed_ip       = models.GenericIPAddressField(null=True, blank=True)
    session_start   = models.DateTimeField()
    session_stop    = models.DateTimeField(null=True, blank=True)
    bytes_in        = models.BigIntegerField(default=0)
    bytes_out       = models.BigIntegerField(default=0)
    is_active       = models.BooleanField(default=True)

    class Meta:
        ordering = ['-session_start']


class BandwidthLog(models.Model):
    """Daily bandwidth usage logs"""
    customer    = models.ForeignKey('customers.Customer', on_delete=models.CASCADE,
                                    related_name='bandwidth_logs')
    date        = models.DateField()
    bytes_in    = models.BigIntegerField(default=0)
    bytes_out   = models.BigIntegerField(default=0)
    total_bytes = models.BigIntegerField(default=0)

    class Meta:
        unique_together = ['customer', 'date']
        ordering = ['-date']


class NetworkAlert(models.Model):
    """Network monitoring alerts"""
    SEVERITY = [
        ('critical', 'Critical'),
        ('high',     'High'),
        ('medium',   'Medium'),
        ('low',      'Low'),
        ('info',     'Info'),
    ]
    device      = models.ForeignKey(NetworkDevice, on_delete=models.CASCADE,
                                    related_name='alerts', null=True, blank=True)
    customer    = models.ForeignKey('customers.Customer', on_delete=models.CASCADE,
                                    related_name='network_alerts', null=True, blank=True)
    severity    = models.CharField(max_length=20, choices=SEVERITY, default='info')
    title       = models.CharField(max_length=200)
    message     = models.TextField()
    is_resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(null=True, blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)
