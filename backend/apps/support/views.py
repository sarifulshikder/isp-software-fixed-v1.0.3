from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from .models import Ticket, TicketComment, FieldVisit, KnowledgeBase
from .serializers import TicketListSerializer, TicketDetailSerializer, TicketCommentSerializer, FieldVisitSerializer, KnowledgeBaseSerializer

class TicketViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    filter_backends    = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields   = ['status','priority','category','assigned_to']
    search_fields      = ['ticket_number','subject','customer__first_name']
    ordering           = ['-created_at']

    def get_queryset(self):
        return Ticket.objects.select_related('customer','assigned_to').all()

    def get_serializer_class(self):
        return TicketListSerializer if self.action == 'list' else TicketDetailSerializer

    @action(detail=True, methods=['post'])
    def add_comment(self, request, pk=None):
        ticket = self.get_object()
        s = TicketCommentSerializer(data=request.data)
        if s.is_valid():
            s.save(ticket=ticket, author=request.user)
            return Response(s.data, status=status.HTTP_201_CREATED)
        return Response(s.errors, status=400)

    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        ticket = self.get_object()
        ticket.status = 'resolved'
        ticket.resolution = request.data.get('resolution', '')
        ticket.resolved_at = timezone.now()
        ticket.save(update_fields=['status','resolution','resolved_at'])
        return Response({'status': 'resolved'})

    @action(detail=False, methods=['get'])
    def stats(self, request):
        qs = Ticket.objects.all()
        return Response({
            'open':       qs.filter(status='open').count(),
            'in_progress':qs.filter(status='in_progress').count(),
            'resolved':   qs.filter(status='resolved').count(),
            'sla_breached':qs.filter(sla_breached=True, status__in=['open','in_progress']).count(),
        })

class KnowledgeBaseViewSet(viewsets.ModelViewSet):
    queryset           = KnowledgeBase.objects.all()
    serializer_class   = KnowledgeBaseSerializer
    permission_classes = [IsAuthenticated]
    filter_backends    = [filters.SearchFilter]
    search_fields      = ['title','content']
