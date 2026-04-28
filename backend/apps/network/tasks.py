from celery import shared_task
from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)

@shared_task(queue='network')
def check_device_health():
    from .models import NetworkDevice
    from django.utils import timezone
    for device in NetworkDevice.objects.exclude(ip_address=None):
        import subprocess
        r = subprocess.run(['ping','-c','1','-W','2', device.ip_address],
                           capture_output=True)
        device.status = 'online' if r.returncode == 0 else 'offline'
        device.last_seen = timezone.now() if r.returncode == 0 else device.last_seen
        device.save(update_fields=['status','last_seen'])
    return 'done'

@shared_task(queue='network')
def sync_radius_sessions():
    logger.info("Syncing RADIUS sessions")
    return 'done'

@shared_task(queue='network')
def collect_bandwidth_stats():
    logger.info("Collecting bandwidth stats")
    return 'done'

@shared_task(queue='network')
def suspend_customer_radius(customer_id):
    logger.info(f"Suspending RADIUS for customer {customer_id}")
    return 'done'
