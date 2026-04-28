from django.contrib import admin
from .models import ProductCategory, Product, StockMovement, CustomerEquipment

@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ['name']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display  = ['code', 'name', 'brand', 'stock_quantity', 'min_stock', 'unit_cost']
    list_filter   = ['category']
    search_fields = ['name', 'code', 'brand']

@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ['product', 'type', 'quantity', 'performed_by', 'created_at']
    list_filter  = ['type']

@admin.register(CustomerEquipment)
class CustomerEquipmentAdmin(admin.ModelAdmin):
    list_display = ['customer', 'product', 'serial_number', 'is_returned', 'assigned_at']
    list_filter  = ['is_returned']
