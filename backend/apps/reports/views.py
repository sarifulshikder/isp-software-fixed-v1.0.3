from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Sum, Count, Avg
from datetime import timedelta
from .models import ReportTemplate
from .serializers import ReportTemplateSerializer


class ReportViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def revenue(self, request):
        from apps.payments.models import Payment
        from apps.billing.models import Invoice
        today   = timezone.now().date()
        month_start = today.replace(day=1)

        monthly_payments = Payment.objects.filter(
            payment_date__date__gte=month_start,
            status='completed'
        )
        return Response({
            'this_month': {
                'total':    monthly_payments.aggregate(t=Sum('amount'))['t'] or 0,
                'count':    monthly_payments.count(),
                'by_method': list(
                    monthly_payments.values('method').annotate(
                        total=Sum('amount'), count=Count('id')
                    )
                ),
            },
            'outstanding': Invoice.objects.filter(
                status__in=['pending', 'overdue']
            ).aggregate(t=Sum('balance_due'))['t'] or 0,
            'overdue_count': Invoice.objects.filter(status='overdue').count(),
        })

    @action(detail=False, methods=['get'])
    def customers(self, request):
        from apps.customers.models import Customer
        from django.db.models.functions import TruncMonth
        qs = Customer.objects.all()
        return Response({
            'total':        qs.count(),
            'active':       qs.filter(status='active').count(),
            'new_this_month': qs.filter(
                created_at__month=timezone.now().month,
                created_at__year=timezone.now().year
            ).count(),
            'by_package': list(
                qs.values('package__name').annotate(count=Count('id')).order_by('-count')
            ),
            'by_zone': list(
                qs.values('zone__name').annotate(count=Count('id')).order_by('-count')
            ),
            'by_status': list(
                qs.values('status').annotate(count=Count('id'))
            ),
        })

    @action(detail=False, methods=['get'])
    def network(self, request):
        from apps.network.models import NetworkDevice, RADIUSSession, BandwidthLog
        return Response({
            'devices': {
                'total':   NetworkDevice.objects.count(),
                'online':  NetworkDevice.objects.filter(status='online').count(),
                'offline': NetworkDevice.objects.filter(status='offline').count(),
            },
            'active_sessions': RADIUSSession.objects.filter(is_active=True).count(),
        })

    @action(detail=False, methods=['get'])
    def support(self, request):
        from apps.support.models import Ticket
        qs = Ticket.objects.all()
        return Response({
            'total':          qs.count(),
            'open':           qs.filter(status='open').count(),
            'resolved':       qs.filter(status='resolved').count(),
            'sla_breached':   qs.filter(sla_breached=True).count(),
            'avg_resolution': 'N/A',
            'by_category': list(qs.values('category').annotate(count=Count('id'))),
        })


class ReportTemplateViewSet(viewsets.ModelViewSet):
    serializer_class   = ReportTemplateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ReportTemplate.objects.filter(created_by=self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
