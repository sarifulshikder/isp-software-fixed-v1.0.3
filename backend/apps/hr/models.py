from django.db import models
from django.conf import settings


class Department(models.Model):
    name    = models.CharField(max_length=100)
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='managed_departments'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class StaffProfile(models.Model):
    user        = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='staff_profile')
    department  = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    designation = models.CharField(max_length=100)
    employee_id = models.CharField(max_length=20, unique=True)
    join_date   = models.DateField()
    salary      = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    nid         = models.CharField(max_length=20, blank=True)
    address     = models.TextField(blank=True)
    emergency_contact = models.CharField(max_length=100, blank=True)
    is_active   = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.employee_id} - {self.user.get_full_name()}"


class Attendance(models.Model):
    STATUS_CHOICES = [
        ('present',  'Present'),
        ('absent',   'Absent'),
        ('late',     'Late'),
        ('half_day', 'Half Day'),
        ('holiday',  'Holiday'),
        ('leave',    'On Leave'),
    ]
    staff     = models.ForeignKey(StaffProfile, on_delete=models.CASCADE, related_name='attendance_records')
    date      = models.DateField()
    check_in  = models.TimeField(null=True, blank=True)
    check_out = models.TimeField(null=True, blank=True)
    status    = models.CharField(max_length=20, choices=STATUS_CHOICES, default='present')
    notes     = models.TextField(blank=True)

    class Meta:
        unique_together = ['staff', 'date']
        ordering = ['-date']

    def __str__(self):
        return f"{self.staff} - {self.date} ({self.status})"


class LeaveRequest(models.Model):
    TYPE_CHOICES   = [('annual','Annual'),('sick','Sick'),('casual','Casual'),('other','Other')]
    STATUS_CHOICES = [('pending','Pending'),('approved','Approved'),('rejected','Rejected')]

    staff       = models.ForeignKey(StaffProfile, on_delete=models.CASCADE, related_name='leave_requests')
    type        = models.CharField(max_length=20, choices=TYPE_CHOICES)
    start_date  = models.DateField()
    end_date    = models.DateField()
    reason      = models.TextField()
    status      = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.staff} - {self.type} ({self.status})"
