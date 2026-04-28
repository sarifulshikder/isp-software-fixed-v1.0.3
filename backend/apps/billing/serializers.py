from rest_framework import serializers
from .models import Invoice, InvoiceItem, CreditNote, Discount


class InvoiceItemSerializer(serializers.ModelSerializer):
    class Meta:
        model  = InvoiceItem
        fields = '__all__'


class InvoiceListSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.full_name', read_only=True)
    customer_id   = serializers.CharField(source='customer.customer_id', read_only=True)

    class Meta:
        model  = Invoice
        fields = [
            'id','invoice_number','customer_name','customer_id','invoice_type',
            'status','total','amount_paid','balance_due','due_date','created_at',
        ]


class InvoiceDetailSerializer(serializers.ModelSerializer):
    items         = InvoiceItemSerializer(many=True, read_only=True)
    customer_name = serializers.CharField(source='customer.full_name', read_only=True)
    is_overdue    = serializers.BooleanField(read_only=True)

    class Meta:
        model  = Invoice
        fields = '__all__'
        read_only_fields = ['invoice_number','created_at','updated_at']


class InvoiceCreateSerializer(serializers.ModelSerializer):
    items = InvoiceItemSerializer(many=True, required=False)

    class Meta:
        model   = Invoice
        exclude = ['invoice_number','created_at','updated_at','amount_paid','balance_due']

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        invoice    = Invoice.objects.create(**validated_data)
        for item in items_data:
            InvoiceItem.objects.create(invoice=invoice, **item)
        return invoice


class DiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Discount
        fields = '__all__'


class CreditNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model  = CreditNote
        fields = '__all__'
