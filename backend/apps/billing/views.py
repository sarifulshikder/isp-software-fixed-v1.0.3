from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from .models import Invoice, Discount, CreditNote
from .serializers import (
    InvoiceListSerializer, InvoiceDetailSerializer,
    InvoiceCreateSerializer, DiscountSerializer, CreditNoteSerializer,
)
from .tasks import generate_monthly_invoices, apply_late_fees, auto_suspend_customers


class InvoiceViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    filter_backends    = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields   = ['status', 'invoice_type', 'customer']
    search_fields      = ['invoice_number', 'customer__first_name', 'customer__customer_id']
    ordering           = ['-created_at']

    def get_queryset(self):
        return Invoice.objects.select_related('customer').all()

    def get_serializer_class(self):
        if self.action == 'list':
            return InvoiceListSerializer
        if self.action in ['create', 'update', 'partial_update']:
            return InvoiceCreateSerializer
        return InvoiceDetailSerializer

    @action(detail=True, methods=['post'])
    def waive(self, request, pk=None):
        invoice = self.get_object()
        reason  = request.data.get('reason', '')
        invoice.status = 'waived'
        invoice.internal_notes = f"Waived: {reason}"
        invoice.save(update_fields=['status', 'internal_notes'])
        return Response({'status': 'waived'})

    @action(detail=True, methods=['post'])
    def send_reminder(self, request, pk=None):
        invoice = self.get_object()
        from apps.notifications.tasks import send_invoice_reminder
        send_invoice_reminder.delay(str(invoice.id))
        return Response({'sent': True})

    @action(detail=False, methods=['get'])
    def summary(self, request):
        from django.db.models import Sum, Count
        qs = Invoice.objects.all()
        return Response({
            'total_invoices':    qs.count(),
            'pending':           qs.filter(status='pending').count(),
            'overdue':           qs.filter(status='overdue').count(),
            'paid':              qs.filter(status='paid').count(),
            'total_billed':      qs.aggregate(t=Sum('total'))['t'] or 0,
            'total_collected':   qs.aggregate(t=Sum('amount_paid'))['t'] or 0,
            'total_outstanding': qs.filter(status__in=['pending','overdue']).aggregate(t=Sum('balance_due'))['t'] or 0,
        })

    @action(detail=False, methods=['post'])
    def run_billing(self, request):
        generate_monthly_invoices.delay()
        return Response({'task': 'queued'})

    @action(detail=False, methods=['post'])
    def run_late_fees(self, request):
        apply_late_fees.delay()
        return Response({'task': 'queued'})


class DiscountViewSet(viewsets.ModelViewSet):
    queryset           = Discount.objects.all()
    serializer_class   = DiscountSerializer
    permission_classes = [IsAuthenticated]
