from django.contrib import admin
from .models import IPPool, IPAddress, NetworkDevice, RADIUSSession, BandwidthLog, NetworkAlert


@admin.register(IPPool)
class IPPoolAdmin(admin.ModelAdmin):
    list_display = ['name', 'network', 'gateway', 'vlan_id', 'is_active']
    list_filter  = ['is_active']


@admin.register(IPAddress)
class IPAddressAdmin(admin.ModelAdmin):
    list_display  = ['address', 'pool', 'status', 'customer', 'assigned_at']
    list_filter   = ['status', 'pool']
    search_fields = ['address']


@admin.register(NetworkDevice)
class NetworkDeviceAdmin(admin.ModelAdmin):
    list_display  = ['name', 'device_type', 'ip_address', 'status', 'location', 'last_seen']
    list_filter   = ['device_type', 'status']
    search_fields = ['name', 'ip_address', 'serial']


@admin.register(RADIUSSession)
class RADIUSSessionAdmin(admin.ModelAdmin):
    list_display = ['username', 'customer', 'framed_ip', 'nas_ip', 'session_start', 'is_active']
    list_filter  = ['is_active']
    search_fields = ['username', 'framed_ip']


@admin.register(NetworkAlert)
class NetworkAlertAdmin(admin.ModelAdmin):
    list_display = ['title', 'severity', 'device', 'is_resolved', 'created_at']
    list_filter  = ['severity', 'is_resolved']

admin.site.register(BandwidthLog)
