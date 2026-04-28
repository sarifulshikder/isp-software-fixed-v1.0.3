"""
ISP Software - Celery Configuration
"""
from celery import Celery
from celery.schedules import crontab
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')

app = Celery('isp_software')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# ─────────────────────────────────────────
# Scheduled Tasks (Celery Beat)
# ─────────────────────────────────────────
app.conf.beat_schedule = {

    # Generate invoices at midnight every day
    'generate-monthly-invoices': {
        'task': 'apps.billing.tasks.generate_monthly_invoices',
        'schedule': crontab(hour=0, minute=1),
    },

    # Apply late fees every morning
    'apply-late-fees': {
        'task': 'apps.billing.tasks.apply_late_fees',
        'schedule': crontab(hour=9, minute=0),
    },

    # Auto suspend overdue customers at 10 AM
    'auto-suspend-customers': {
        'task': 'apps.billing.tasks.auto_suspend_customers',
        'schedule': crontab(hour=10, minute=0),
    },

    # Check expiring packages every morning
    'check-expiring-packages': {
        'task': 'apps.billing.tasks.check_expiring_packages',
        'schedule': crontab(hour=8, minute=0),
    },

    # Daily revenue report at 11 PM
    'daily-revenue-report': {
        'task': 'apps.billing.tasks.generate_daily_revenue_report',
        'schedule': crontab(hour=23, minute=0),
    },

    # Send bill reminders 3 days before due date
    'send-bill-reminders': {
        'task': 'apps.notifications.tasks.send_bill_reminders',
        'schedule': crontab(hour=10, minute=30),
    },

    # Network device health check every 5 minutes
    'network-health-check': {
        'task': 'apps.network.tasks.check_device_health',
        'schedule': crontab(minute='*/5'),
    },

    # Sync RADIUS sessions every 10 minutes
    'sync-radius-sessions': {
        'task': 'apps.network.tasks.sync_radius_sessions',
        'schedule': crontab(minute='*/10'),
    },

    # Collect bandwidth stats every hour
    'collect-bandwidth-stats': {
        'task': 'apps.network.tasks.collect_bandwidth_stats',
        'schedule': crontab(minute=0),
    },

    # Check SLA breaches every 30 minutes
    'check-sla-breaches': {
        'task': 'apps.support.tasks.check_sla_breaches',
        'schedule': crontab(minute='*/30'),
    },

    # Cleanup old logs weekly
    'cleanup-old-logs': {
        'task': 'utils.tasks.cleanup_old_logs',
        'schedule': crontab(day_of_week=0, hour=2, minute=0),
    },

    # Cleanup expired JWT blacklisted tokens daily
    'flush-expired-tokens': {
        'task': 'utils.tasks.flush_expired_tokens',
        'schedule': crontab(hour=3, minute=0),
    },
}

app.conf.timezone = 'Asia/Dhaka'
