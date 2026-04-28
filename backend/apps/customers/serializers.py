from rest_framework import serializers
from .models import Customer, Zone, CustomerDocument, CustomerNote


class ZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Zone
        fields = '__all__'


class CustomerDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerDocument
        fields = '__all__'
        read_only_fields = ['verified_by']


class CustomerNoteSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)

    class Meta:
        model = CustomerNote
        fields = '__all__'
        read_only_fields = ['author']


class CustomerListSerializer(serializers.ModelSerializer):
    package_name = serializers.CharField(source='package.name', read_only=True)
    zone_name    = serializers.CharField(source='zone.name', read_only=True)

    class Meta:
        model  = Customer
        fields = [
            'id','customer_id','first_name','last_name','phone','email',
            'status','package_name','zone_name','connection_date',
            'expiry_date','advance_balance','created_at',
        ]


class CustomerDetailSerializer(serializers.ModelSerializer):
    documents      = CustomerDocumentSerializer(many=True, read_only=True)
    customer_notes = CustomerNoteSerializer(many=True, read_only=True)
    package_name   = serializers.CharField(source='package.name', read_only=True)
    package_price  = serializers.DecimalField(source='package.price', max_digits=10, decimal_places=2, read_only=True)
    zone_name      = serializers.CharField(source='zone.name', read_only=True)
    is_expired     = serializers.BooleanField(read_only=True)

    class Meta:
        model  = Customer
        fields = '__all__'
        read_only_fields = ['customer_id','created_by','created_at','updated_at']


class CustomerCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model   = Customer
        exclude = ['customer_id','created_by','created_at','updated_at']

    def create(self, validated_data):
        req = self.context.get('request')
        if req and req.user:
            validated_data['created_by'] = req.user
        return super().create(validated_data)
