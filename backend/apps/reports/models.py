from django.db import models
from django.conf import settings


class ReportTemplate(models.Model):
    """Saved custom report configurations"""
    REPORT_TYPES = [
        ('revenue',   'Revenue Report'),
        ('customers', 'Customer Report'),
        ('network',   'Network Report'),
        ('payments',  'Payment Report'),
        ('inventory', 'Inventory Report'),
    ]
    name        = models.CharField(max_length=100)
    report_type = models.CharField(max_length=30, choices=REPORT_TYPES)
    filters     = models.JSONField(default=dict)
    columns     = models.JSONField(default=list)
    created_by  = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    is_shared   = models.BooleanField(default=False)
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.report_type})"
