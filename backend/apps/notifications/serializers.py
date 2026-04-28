from rest_framework import serializers
from .models import NotificationTemplate, NotificationLog


class NotificationTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model  = NotificationTemplate
        fields = '__all__'


class NotificationLogSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.full_name', read_only=True)

    class Meta:
        model  = NotificationLog
        fields = '__all__'
