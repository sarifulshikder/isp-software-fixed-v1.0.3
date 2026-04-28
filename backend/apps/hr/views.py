from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from .models import Department, StaffProfile, Attendance, LeaveRequest
from .serializers import (
    DepartmentSerializer, StaffProfileSerializer,
    AttendanceSerializer, LeaveRequestSerializer
)


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset           = Department.objects.all()
    serializer_class   = DepartmentSerializer
    permission_classes = [IsAuthenticated]


class StaffProfileViewSet(viewsets.ModelViewSet):
    queryset           = StaffProfile.objects.select_related('user', 'department').all()
    serializer_class   = StaffProfileSerializer
    permission_classes = [IsAuthenticated]
    filter_backends    = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields   = ['department', 'is_active']
    search_fields      = ['user__first_name', 'user__last_name', 'employee_id', 'designation']

    @action(detail=False, methods=['get'])
    def stats(self, request):
        qs = StaffProfile.objects.all()
        return Response({
            'total':    qs.count(),
            'active':   qs.filter(is_active=True).count(),
            'inactive': qs.filter(is_active=False).count(),
        })


class AttendanceViewSet(viewsets.ModelViewSet):
    queryset           = Attendance.objects.select_related('staff__user').all()
    serializer_class   = AttendanceSerializer
    permission_classes = [IsAuthenticated]
    filter_backends    = [DjangoFilterBackend]
    filterset_fields   = ['staff', 'date', 'status']

    @action(detail=False, methods=['post'])
    def check_in(self, request):
        staff_id = request.data.get('staff_id')
        today    = timezone.now().date()
        att, _   = Attendance.objects.get_or_create(
            staff_id=staff_id, date=today,
            defaults={'check_in': timezone.now().time()}
        )
        return Response(AttendanceSerializer(att).data)

    @action(detail=False, methods=['post'])
    def check_out(self, request):
        staff_id = request.data.get('staff_id')
        today    = timezone.now().date()
        try:
            att = Attendance.objects.get(staff_id=staff_id, date=today)
            att.check_out = timezone.now().time()
            att.save(update_fields=['check_out'])
            return Response(AttendanceSerializer(att).data)
        except Attendance.DoesNotExist:
            return Response({'error': 'No check-in found for today.'}, status=400)


class LeaveRequestViewSet(viewsets.ModelViewSet):
    queryset           = LeaveRequest.objects.select_related('staff__user').all()
    serializer_class   = LeaveRequestSerializer
    permission_classes = [IsAuthenticated]
    filter_backends    = [DjangoFilterBackend]
    filterset_fields   = ['status', 'type', 'staff']

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        leave = self.get_object()
        leave.status      = 'approved'
        leave.approved_by = request.user
        leave.save(update_fields=['status', 'approved_by'])
        return Response({'status': 'approved'})

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        leave = self.get_object()
        leave.status      = 'rejected'
        leave.approved_by = request.user
        leave.save(update_fields=['status', 'approved_by'])
        return Response({'status': 'rejected'})
