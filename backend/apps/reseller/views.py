from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Reseller, ResellerCommission
from .serializers import ResellerSerializer, ResellerCommissionSerializer


class ResellerViewSet(viewsets.ModelViewSet):
    queryset           = Reseller.objects.select_related('user').all()
    serializer_class   = ResellerSerializer
    permission_classes = [IsAuthenticated]
    filter_backends    = [DjangoFilterBackend, filters.SearchFilter]
    search_fields      = ['company_name', 'contact_person', 'phone', 'email']
    filterset_fields   = ['is_active']

    @action(detail=False, methods=['get'])
    def stats(self, request):
        qs = Reseller.objects.all()
        return Response({
            'total':    qs.count(),
            'active':   qs.filter(is_active=True).count(),
            'inactive': qs.filter(is_active=False).count(),
        })

    @action(detail=True, methods=['get'])
    def customers(self, request, pk=None):
        reseller = self.get_object()
        from apps.customers.models import Customer
        from apps.customers.serializers import CustomerListSerializer
        customers = Customer.objects.filter(reseller=reseller)
        return Response(CustomerListSerializer(customers, many=True).data)


class ResellerCommissionViewSet(viewsets.ModelViewSet):
    queryset           = ResellerCommission.objects.select_related('reseller').all()
    serializer_class   = ResellerCommissionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends    = [DjangoFilterBackend]
    filterset_fields   = ['reseller', 'is_paid']
