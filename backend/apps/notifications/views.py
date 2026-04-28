from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import NotificationTemplate, NotificationLog
from .serializers import NotificationTemplateSerializer, NotificationLogSerializer


class NotificationTemplateViewSet(viewsets.ModelViewSet):
    queryset           = NotificationTemplate.objects.all()
    serializer_class   = NotificationTemplateSerializer
    permission_classes = [IsAuthenticated]
    filter_backends    = [DjangoFilterBackend]
    filterset_fields   = ['channel', 'event', 'is_active']


class NotificationLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset           = NotificationLog.objects.select_related('customer').all()
    serializer_class   = NotificationLogSerializer
    permission_classes = [IsAuthenticated]
    filter_backends    = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields   = ['channel', 'status']
    search_fields      = ['recipient', 'customer__first_name']

    @action(detail=False, methods=['post'])
    def send_bulk(self, request):
        """Send bulk SMS/Email to customer group"""
        channel    = request.data.get('channel', 'sms')
        message    = request.data.get('message', '')
        customer_filter = request.data.get('filter', {})
        from apps.customers.models import Customer
        customers = Customer.objects.filter(status='active', **customer_filter)
        queued = 0
        for c in customers:
            from .tasks import send_sms_notification
            send_sms_notification.delay(str(c.id), message)
            queued += 1
        return Response({'queued': queued})
