from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import IPPool, IPAddress, NetworkDevice, RADIUSSession, BandwidthLog, NetworkAlert
from .serializers import (
    IPPoolSerializer, IPAddressSerializer, NetworkDeviceSerializer,
    RADIUSSessionSerializer, BandwidthLogSerializer, NetworkAlertSerializer,
)

class IPPoolViewSet(viewsets.ModelViewSet):
    queryset           = IPPool.objects.all()
    serializer_class   = IPPoolSerializer
    permission_classes = [IsAuthenticated]

class IPAddressViewSet(viewsets.ModelViewSet):
    queryset           = IPAddress.objects.select_related('pool', 'customer').all()
    serializer_class   = IPAddressSerializer
    permission_classes = [IsAuthenticated]
    filter_backends    = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields   = ['status', 'pool']
    search_fields      = ['address']

class NetworkDeviceViewSet(viewsets.ModelViewSet):
    queryset           = NetworkDevice.objects.all()
    serializer_class   = NetworkDeviceSerializer
    permission_classes = [IsAuthenticated]
    filter_backends    = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields   = ['device_type', 'status']
    search_fields      = ['name', 'ip_address', 'serial']

    @action(detail=True, methods=['post'])
    def ping(self, request, pk=None):
        device = self.get_object()
        import subprocess
        result = subprocess.run(['ping','-c','2','-W','2', device.ip_address or ''],
                                capture_output=True, text=True)
        return Response({'online': result.returncode == 0, 'output': result.stdout[:300]})

class RADIUSSessionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset           = RADIUSSession.objects.select_related('customer').filter(is_active=True)
    serializer_class   = RADIUSSessionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends    = [DjangoFilterBackend, filters.SearchFilter]
    search_fields      = ['username', 'framed_ip']

class NetworkAlertViewSet(viewsets.ModelViewSet):
    queryset           = NetworkAlert.objects.all().order_by('-created_at')
    serializer_class   = NetworkAlertSerializer
    permission_classes = [IsAuthenticated]
    filter_backends    = [DjangoFilterBackend]
    filterset_fields   = ['severity', 'is_resolved']

    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        from django.utils import timezone
        alert = self.get_object()
        alert.is_resolved = True
        alert.resolved_at = timezone.now()
        alert.save(update_fields=['is_resolved','resolved_at'])
        return Response({'resolved': True})
