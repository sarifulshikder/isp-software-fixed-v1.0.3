"""
Periodic housekeeping tasks shared across the project.
"""
import os
import time
from celery import shared_task
from celery.utils.log import get_task_logger
from django.conf import settings
from django.core.management import call_command

logger = get_task_logger(__name__)


@shared_task
def cleanup_old_logs(days: int = 14):
    """Delete rotating log files older than `days` days from the logs directory."""
    log_dir = getattr(settings, 'BASE_DIR', None)
    if not log_dir:
        return {'deleted': 0, 'reason': 'BASE_DIR missing'}
    log_dir = os.path.join(str(log_dir), 'logs')
    if not os.path.isdir(log_dir):
        return {'deleted': 0, 'reason': 'no log dir'}

    cutoff = time.time() - (days * 86400)
    deleted = 0
    for name in os.listdir(log_dir):
        path = os.path.join(log_dir, name)
        try:
            if os.path.isfile(path) and os.path.getmtime(path) < cutoff:
                os.remove(path)
                deleted += 1
        except OSError as exc:
            logger.warning(f"Could not remove log {path}: {exc}")
    logger.info(f"cleanup_old_logs removed {deleted} files older than {days}d")
    return {'deleted': deleted}


@shared_task
def flush_expired_tokens():
    """Remove blacklisted JWT tokens whose original lifetime has expired."""
    try:
        call_command('flushexpiredtokens')
        return {'status': 'ok'}
    except Exception as exc:
        logger.error(f"flushexpiredtokens failed: {exc}")
        return {'status': 'error', 'error': str(exc)}
