from rest_framework import serializers
from django.db import transaction
from django.db.models import F
from .models import ProductCategory, Product, StockMovement, CustomerEquipment


class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model  = ProductCategory
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    is_low_stock  = serializers.BooleanField(read_only=True)

    class Meta:
        model  = Product
        fields = '__all__'
        read_only_fields = ['created_at']


# Movement types that increase stock vs. decrease stock
INCREASE_TYPES = {'purchase', 'return', 'retrieved', 'adjustment'}
DECREASE_TYPES = {'issue', 'assigned', 'damaged'}


class StockMovementSerializer(serializers.ModelSerializer):
    product_name      = serializers.CharField(source='product.name', read_only=True)
    performed_by_name = serializers.CharField(source='performed_by.get_full_name', read_only=True)

    class Meta:
        model  = StockMovement
        fields = '__all__'
        read_only_fields = ['performed_by', 'created_at']

    def validate(self, attrs):
        qty = attrs.get('quantity', 0)
        if qty <= 0:
            raise serializers.ValidationError({'quantity': 'Quantity must be positive.'})
        return attrs

    def create(self, validated_data):
        with transaction.atomic():
            movement = super().create(validated_data)
            mtype = movement.type
            qty = movement.quantity
            if mtype in INCREASE_TYPES:
                Product.objects.filter(pk=movement.product_id).update(
                    stock_quantity=F('stock_quantity') + qty
                )
            elif mtype in DECREASE_TYPES:
                # Refresh to get the current stock, then validate
                product = Product.objects.select_for_update().get(pk=movement.product_id)
                if product.stock_quantity < qty:
                    raise serializers.ValidationError(
                        {'quantity': f'Insufficient stock (have {product.stock_quantity}, need {qty}).'}
                    )
                Product.objects.filter(pk=movement.product_id).update(
                    stock_quantity=F('stock_quantity') - qty
                )
        return movement


class CustomerEquipmentSerializer(serializers.ModelSerializer):
    product_name  = serializers.CharField(source='product.name', read_only=True)
    customer_name = serializers.CharField(source='customer.full_name', read_only=True)

    class Meta:
        model  = CustomerEquipment
        fields = '__all__'
