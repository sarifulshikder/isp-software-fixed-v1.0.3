from rest_framework import serializers
from .models import Package, PackagePriceHistory

class PackageSerializer(serializers.ModelSerializer):
    speed_display    = serializers.CharField(source='get_speed_display', read_only=True)
    customer_count   = serializers.SerializerMethodField()

    class Meta:
        model  = Package
        fields = '__all__'
        read_only_fields = ['created_at','updated_at']

    def get_customer_count(self, obj):
        return obj.customers.filter(status='active').count()
