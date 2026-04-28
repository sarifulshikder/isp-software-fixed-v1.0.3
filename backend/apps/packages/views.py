from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from .models import Package
from .serializers import PackageSerializer

class PackageViewSet(viewsets.ModelViewSet):
    queryset           = Package.objects.all()
    serializer_class   = PackageSerializer
    permission_classes = [IsAuthenticated]
    filter_backends    = [filters.SearchFilter, filters.OrderingFilter]
    search_fields      = ['name', 'code']
    ordering           = ['sort_order', 'price']
