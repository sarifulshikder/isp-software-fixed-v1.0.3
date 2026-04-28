from rest_framework import serializers
from .models import Ticket, TicketComment, FieldVisit, KnowledgeBase

class TicketCommentSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)
    class Meta:
        model = TicketComment
        fields = '__all__'
        read_only_fields = ['author']

class TicketListSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.full_name', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    class Meta:
        model = Ticket
        fields = ['id','ticket_number','customer_name','subject','category','priority','status','assigned_to_name','sla_deadline','sla_breached','created_at']

class TicketDetailSerializer(serializers.ModelSerializer):
    comments = TicketCommentSerializer(many=True, read_only=True)
    customer_name = serializers.CharField(source='customer.full_name', read_only=True)
    class Meta:
        model = Ticket
        fields = '__all__'
        read_only_fields = ['ticket_number','created_at','updated_at']

class FieldVisitSerializer(serializers.ModelSerializer):
    class Meta:
        model = FieldVisit
        fields = '__all__'

class KnowledgeBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = KnowledgeBase
        fields = '__all__'
