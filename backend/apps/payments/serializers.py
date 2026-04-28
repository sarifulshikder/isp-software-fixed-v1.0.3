from rest_framework import serializers
from .models import Payment, Refund


class PaymentSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.full_name', read_only=True)
    customer_code = serializers.CharField(source='customer.customer_id', read_only=True)
    collected_by_name = serializers.CharField(source='collected_by.get_full_name', read_only=True)

    class Meta:
        model  = Payment
        fields = '__all__'
        read_only_fields = ['payment_number', 'created_at']


class RefundSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Refund
        fields = '__all__'
        read_only_fields = ['processed_by', 'processed_at']
