from celery import shared_task
from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)

@shared_task
def check_sla_breaches():
    from .models import Ticket
    from django.utils import timezone
    breached = Ticket.objects.filter(
        status__in=['open','in_progress'],
        sla_deadline__lt=timezone.now(),
        sla_breached=False
    )
    count = 0
    for t in breached:
        t.sla_breached = True
        t.save(update_fields=['sla_breached'])
        count += 1
    return {'breached': count}
