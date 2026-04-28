from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import F, Sum, Count
from .models import ProductCategory, Product, StockMovement, CustomerEquipment
from .serializers import (
    ProductCategorySerializer, ProductSerializer,
    StockMovementSerializer, CustomerEquipmentSerializer
)


class ProductCategoryViewSet(viewsets.ModelViewSet):
    queryset           = ProductCategory.objects.all()
    serializer_class   = ProductCategorySerializer
    permission_classes = [IsAuthenticated]


class ProductViewSet(viewsets.ModelViewSet):
    queryset           = Product.objects.select_related('category').all()
    serializer_class   = ProductSerializer
    permission_classes = [IsAuthenticated]
    filter_backends    = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields   = ['category']
    search_fields      = ['name', 'code', 'brand', 'model']

    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        products = Product.objects.filter(stock_quantity__lte=F('min_stock'))
        return Response(ProductSerializer(products, many=True).data)

    @action(detail=False, methods=['get'])
    def summary(self, request):
        qs = Product.objects.all()
        return Response({
            'total_products': qs.count(),
            'low_stock':      qs.filter(stock_quantity__lte=F('min_stock')).count(),
            'total_value':    qs.aggregate(v=Sum(F('unit_cost') * F('stock_quantity')))['v'] or 0,
        })


class StockMovementViewSet(viewsets.ModelViewSet):
    queryset           = StockMovement.objects.select_related('product', 'performed_by').all()
    serializer_class   = StockMovementSerializer
    permission_classes = [IsAuthenticated]
    filter_backends    = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields   = ['product', 'type']

    def perform_create(self, serializer):
        serializer.save(performed_by=self.request.user)


class CustomerEquipmentViewSet(viewsets.ModelViewSet):
    queryset           = CustomerEquipment.objects.select_related('customer', 'product').all()
    serializer_class   = CustomerEquipmentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends    = [DjangoFilterBackend]
    filterset_fields   = ['customer', 'is_returned']
