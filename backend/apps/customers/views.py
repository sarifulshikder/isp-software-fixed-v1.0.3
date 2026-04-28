from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import timedelta
from .models import Customer, Zone, CustomerDocument, CustomerNote
from .serializers import (
    CustomerListSerializer, CustomerDetailSerializer,
    CustomerCreateSerializer, ZoneSerializer,
    CustomerDocumentSerializer, CustomerNoteSerializer,
)


class CustomerViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    filter_backends    = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields   = ['status', 'zone', 'package', 'connection_type', 'reseller']
    search_fields      = ['customer_id', 'first_name', 'last_name', 'phone', 'email', 'pppoe_username']
    ordering_fields    = ['created_at', 'first_name', 'expiry_date']
    ordering           = ['-created_at']

    def get_queryset(self):
        return Customer.objects.select_related('package', 'zone', 'reseller').all()

    def get_serializer_class(self):
        if self.action == 'list':
            return CustomerListSerializer
        if self.action in ['create', 'update', 'partial_update']:
            return CustomerCreateSerializer
        return CustomerDetailSerializer

    @action(detail=True, methods=['post'])
    def suspend(self, request, pk=None):
        customer = self.get_object()
        customer.status = 'suspended'
        customer.suspension_date = timezone.now().date()
        customer.save(update_fields=['status', 'suspension_date'])
        return Response({'status': 'suspended'})

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        customer = self.get_object()
        customer.status = 'active'
        customer.suspension_date = None
        customer.save(update_fields=['status', 'suspension_date'])
        return Response({'status': 'active'})

    @action(detail=True, methods=['post'])
    def terminate(self, request, pk=None):
        customer = self.get_object()
        customer.status = 'terminated'
        customer.termination_date = timezone.now().date()
        customer.save(update_fields=['status', 'termination_date'])
        return Response({'status': 'terminated'})

    @action(detail=False, methods=['get'])
    def stats(self, request):
        qs = Customer.objects.all()
        return Response({
            'total':      qs.count(),
            'active':     qs.filter(status='active').count(),
            'suspended':  qs.filter(status='suspended').count(),
            'terminated': qs.filter(status='terminated').count(),
            'pending':    qs.filter(status='pending').count(),
            'expiring_soon': qs.filter(
                status='active',
                expiry_date__lte=timezone.now().date() + timedelta(days=3)
            ).count(),
        })

    @action(detail=True, methods=['post'])
    def add_note(self, request, pk=None):
        customer = self.get_object()
        serializer = CustomerNoteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(customer=customer, author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def billing_history(self, request, pk=None):
        customer = self.get_object()
        from apps.billing.serializers import InvoiceListSerializer
        invoices = customer.invoices.all().order_by('-created_at')[:12]
        return Response(InvoiceListSerializer(invoices, many=True).data)

    @action(detail=True, methods=['get'])
    def payment_history(self, request, pk=None):
        customer = self.get_object()
        from apps.payments.serializers import PaymentSerializer
        payments = customer.payments.all().order_by('-payment_date')[:20]
        return Response(PaymentSerializer(payments, many=True).data)


class ZoneViewSet(viewsets.ModelViewSet):
    queryset           = Zone.objects.all()
    serializer_class   = ZoneSerializer
    permission_classes = [IsAuthenticated]
    filter_backends    = [filters.SearchFilter]
    search_fields      = ['name']
