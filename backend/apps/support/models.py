"""
ISP Software - Support & Helpdesk Models
"""
from django.db import models
from django.conf import settings
import uuid


class Ticket(models.Model):
    """Customer support tickets"""

    PRIORITY = [
        ('critical', 'Critical'),
        ('high',     'High'),
        ('medium',   'Medium'),
        ('low',      'Low'),
    ]

    STATUS = [
        ('open',        'Open'),
        ('in_progress', 'In Progress'),
        ('pending',     'Pending Customer'),
        ('resolved',    'Resolved'),
        ('closed',      'Closed'),
        ('escalated',   'Escalated'),
    ]

    CATEGORY = [
        ('no_internet',     'No Internet'),
        ('slow_speed',      'Slow Speed'),
        ('billing',         'Billing Issue'),
        ('installation',    'New Installation'),
        ('upgrade',         'Package Upgrade'),
        ('relocation',      'Relocation'),
        ('device_issue',    'Device Issue'),
        ('other',           'Other'),
    ]

    id              = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ticket_number   = models.CharField(max_length=20, unique=True, editable=False)
    customer        = models.ForeignKey('customers.Customer', on_delete=models.CASCADE,
                                        related_name='tickets')
    category        = models.CharField(max_length=30, choices=CATEGORY)
    priority        = models.CharField(max_length=20, choices=PRIORITY, default='medium')
    status          = models.CharField(max_length=20, choices=STATUS, default='open')

    subject         = models.CharField(max_length=255)
    description     = models.TextField()

    # Assignment
    assigned_to     = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                        null=True, blank=True, related_name='assigned_tickets')
    team            = models.CharField(max_length=50, blank=True)

    # SLA
    sla_hours       = models.PositiveIntegerField(default=24)
    sla_deadline    = models.DateTimeField(null=True, blank=True)
    sla_breached    = models.BooleanField(default=False)

    # Resolution
    resolution      = models.TextField(blank=True)
    resolved_at     = models.DateTimeField(null=True, blank=True)
    closed_at       = models.DateTimeField(null=True, blank=True)
    csat_score      = models.PositiveIntegerField(null=True, blank=True,
                                                   help_text='Customer satisfaction 1-5')
    csat_feedback   = models.TextField(blank=True)

    # Metadata
    created_by      = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                        null=True, related_name='created_tickets')
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'priority']),
            models.Index(fields=['customer']),
            models.Index(fields=['assigned_to']),
        ]

    def __str__(self):
        return f"{self.ticket_number} - {self.subject}"

    def save(self, *args, **kwargs):
        if not self.ticket_number:
            from django.utils import timezone
            ts = timezone.now().strftime('%Y%m%d')
            last = Ticket.objects.filter(
                ticket_number__startswith=f'TKT-{ts}'
            ).count()
            self.ticket_number = f"TKT-{ts}-{last+1:04d}"
        super().save(*args, **kwargs)


class TicketComment(models.Model):
    """Comments on support tickets"""
    ticket      = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='comments')
    author      = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message     = models.TextField()
    is_internal = models.BooleanField(default=False, help_text='Internal note, not visible to customer')
    attachment  = models.FileField(upload_to='tickets/attachments/', null=True, blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']


class FieldVisit(models.Model):
    """Field technician visits"""
    STATUS = [
        ('scheduled', 'Scheduled'),
        ('on_way',    'Technician On The Way'),
        ('arrived',   'Arrived'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    ticket          = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='visits')
    technician      = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    status          = models.CharField(max_length=20, choices=STATUS, default='scheduled')
    scheduled_at    = models.DateTimeField()
    arrived_at      = models.DateTimeField(null=True, blank=True)
    completed_at    = models.DateTimeField(null=True, blank=True)
    notes           = models.TextField(blank=True)
    parts_used      = models.JSONField(default=list)
    visit_charge    = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    lat             = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    lng             = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)


class KnowledgeBase(models.Model):
    """Help articles and FAQs"""
    title       = models.CharField(max_length=255)
    slug        = models.SlugField(unique=True)
    category    = models.CharField(max_length=50)
    content     = models.TextField()
    is_public   = models.BooleanField(default=True)
    views       = models.PositiveIntegerField(default=0)
    helpful     = models.PositiveIntegerField(default=0)
    not_helpful = models.PositiveIntegerField(default=0)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)
