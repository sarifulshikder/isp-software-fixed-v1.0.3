from rest_framework import serializers
from .models import Reseller, ResellerCommission


class ResellerSerializer(serializers.ModelSerializer):
    total_customers  = serializers.IntegerField(read_only=True)
    active_customers = serializers.IntegerField(read_only=True)
    user_email       = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model  = Reseller
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'balance']


class ResellerCommissionSerializer(serializers.ModelSerializer):
    reseller_name = serializers.CharField(source='reseller.company_name', read_only=True)

    class Meta:
        model  = ResellerCommission
        fields = '__all__'
