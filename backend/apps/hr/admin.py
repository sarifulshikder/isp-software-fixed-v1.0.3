from django.contrib import admin
from .models import Department, StaffProfile, Attendance, LeaveRequest

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'manager']

@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    list_display  = ['employee_id', 'user', 'department', 'designation', 'is_active']
    list_filter   = ['department', 'is_active']
    search_fields = ['employee_id', 'user__first_name', 'user__last_name']

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['staff', 'date', 'check_in', 'check_out', 'status']
    list_filter  = ['date', 'status']

@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ['staff', 'type', 'start_date', 'end_date', 'status']
    list_filter  = ['status', 'type']
