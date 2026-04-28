from rest_framework import serializers
from .models import IPPool, IPAddress, NetworkDevice, RADIUSSession, BandwidthLog, NetworkAlert

class IPPoolSerializer(serializers.ModelSerializer):
    total_ips     = serializers.SerializerMethodField()
    available_ips = serializers.SerializerMethodField()
    class Meta:
        model  = IPPool
        fields = '__all__'
    def get_total_ips(self, obj):
        return obj.addresses.count()
    def get_available_ips(self, obj):
        return obj.addresses.filter(status='available').count()

class IPAddressSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.full_name', read_only=True)
    class Meta:
        model  = IPAddress
        fields = '__all__'

class NetworkDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model  = NetworkDevice
        fields = '__all__'

class RADIUSSessionSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.full_name', read_only=True)
    class Meta:
        model  = RADIUSSession
        fields = '__all__'

class BandwidthLogSerializer(serializers.ModelSerializer):
    class Meta:
        model  = BandwidthLog
        fields = '__all__'

class NetworkAlertSerializer(serializers.ModelSerializer):
    class Meta:
        model  = NetworkAlert
        fields = '__all__'
