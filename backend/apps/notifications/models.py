from django.db import models
from django.conf import settings


class NotificationTemplate(models.Model):
    CHANNEL_CHOICES = [
        ('sms',       'SMS'),
        ('email',     'Email'),
        ('whatsapp',  'WhatsApp'),
        ('push',      'Push Notification'),
    ]
    EVENT_CHOICES = [
        ('invoice_created',    'Invoice Created'),
        ('payment_received',   'Payment Received'),
        ('bill_reminder',      'Bill Reminder'),
        ('expiry_reminder',    'Package Expiry Reminder'),
        ('account_suspended',  'Account Suspended'),
        ('account_activated',  'Account Activated'),
        ('ticket_created',     'Ticket Created'),
        ('ticket_resolved',    'Ticket Resolved'),
        ('welcome',            'Welcome Message'),
    ]
    name     = models.CharField(max_length=100)
    event    = models.CharField(max_length=50, choices=EVENT_CHOICES)
    channel  = models.CharField(max_length=20, choices=CHANNEL_CHOICES)
    subject  = models.CharField(max_length=200, blank=True, help_text='For email only')
    body     = models.TextField(help_text='Use {customer_name}, {amount}, {due_date} etc.')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['event', 'channel']

    def __str__(self):
        return f"{self.name} ({self.channel})"


class NotificationLog(models.Model):
    STATUS_CHOICES = [
        ('sent',    'Sent'),
        ('failed',  'Failed'),
        ('pending', 'Pending'),
    ]
    customer    = models.ForeignKey('customers.Customer', on_delete=models.CASCADE,
                                    related_name='notification_logs', null=True, blank=True)
    channel     = models.CharField(max_length=20)
    recipient   = models.CharField(max_length=200)
    subject     = models.CharField(max_length=200, blank=True)
    message     = models.TextField()
    status      = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    error       = models.TextField(blank=True)
    sent_at     = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-sent_at']

    def __str__(self):
        return f"{self.channel} → {self.recipient} ({self.status})"
