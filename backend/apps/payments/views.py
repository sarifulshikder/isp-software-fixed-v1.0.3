from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.db.models import Sum, Count
from .models import Payment, Refund
from .serializers import PaymentSerializer, RefundSerializer


class PaymentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    filter_backends    = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields   = ['method', 'status', 'customer']
    search_fields      = ['payment_number', 'customer__first_name', 'customer__customer_id', 'transaction_id']
    ordering           = ['-payment_date']

    def get_queryset(self):
        return Payment.objects.select_related('customer', 'invoice', 'collected_by').all()

    def get_serializer_class(self):
        return PaymentSerializer

    def perform_create(self, serializer):
        payment = serializer.save(collected_by=self.request.user)
        # Update invoice if linked
        if payment.invoice:
            inv = payment.invoice
            inv.amount_paid = (inv.amount_paid or 0) + payment.amount
            inv.balance_due = inv.total - inv.amount_paid
            if inv.balance_due <= 0:
                inv.status = 'paid'
                inv.paid_date = timezone.now().date()
            else:
                inv.status = 'partial'
            inv.save(update_fields=['amount_paid', 'balance_due', 'status', 'paid_date'])
        # Update customer advance balance if no invoice
        if not payment.invoice and payment.status == 'completed':
            customer = payment.customer
            customer.advance_balance = (customer.advance_balance or 0) + payment.amount
            customer.save(update_fields=['advance_balance'])

    @action(detail=False, methods=['get'])
    def daily_summary(self, request):
        today = timezone.now().date()
        qs = Payment.objects.filter(payment_date__date=today, status='completed')
        return Response({
            'date':         str(today),
            'total':        qs.aggregate(t=Sum('amount'))['t'] or 0,
            'count':        qs.count(),
            'by_method':    list(qs.values('method').annotate(total=Sum('amount'), count=Count('id'))),
        })

    @action(detail=False, methods=['get'])
    def monthly_summary(self, request):
        today = timezone.now().date()
        qs = Payment.objects.filter(
            payment_date__year=today.year,
            payment_date__month=today.month,
            status='completed'
        )
        return Response({
            'month':     today.strftime('%B %Y'),
            'total':     qs.aggregate(t=Sum('amount'))['t'] or 0,
            'count':     qs.count(),
            'by_method': list(qs.values('method').annotate(total=Sum('amount'), count=Count('id'))),
        })

    @action(detail=True, methods=['post'])
    def refund(self, request, pk=None):
        payment = self.get_object()
        amount  = request.data.get('amount', payment.amount)
        reason  = request.data.get('reason', '')
        refund  = Refund.objects.create(
            payment=payment, amount=amount, reason=reason, processed_by=request.user
        )
        payment.status = 'refunded'
        payment.save(update_fields=['status'])
        return Response(RefundSerializer(refund).data, status=status.HTTP_201_CREATED)
