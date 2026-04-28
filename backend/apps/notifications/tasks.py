from celery import shared_task
from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)


@shared_task(queue='notifications')
def send_sms_notification(customer_id, message):
    """Send SMS to a customer via configured gateway"""
    try:
        from apps.customers.models import Customer
        customer = Customer.objects.get(id=customer_id)
        # TODO: Integrate with SMS gateway (Twilio/local provider)
        logger.info(f"SMS to {customer.phone}: {message[:50]}...")
        # Log the notification
        from apps.notifications.models import NotificationLog
        NotificationLog.objects.create(
            customer=customer,
            channel='sms',
            recipient=customer.phone,
            message=message,
            status='sent',
        )
    except Exception as e:
        logger.error(f"SMS failed for customer {customer_id}: {e}")


@shared_task(queue='notifications')
def send_email_notification(customer_id, subject, message):
    """Send email to a customer"""
    try:
        from apps.customers.models import Customer
        from django.core.mail import send_mail
        from django.conf import settings
        customer = Customer.objects.get(id=customer_id)
        if customer.email:
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [customer.email])
            logger.info(f"Email sent to {customer.email}")
            from apps.notifications.models import NotificationLog
            NotificationLog.objects.create(
                customer=customer, channel='email',
                recipient=customer.email, subject=subject,
                message=message, status='sent',
            )
    except Exception as e:
        logger.error(f"Email failed for customer {customer_id}: {e}")


@shared_task(queue='notifications')
def send_bill_reminders():
    from apps.billing.models import Invoice
    from django.utils import timezone
    from datetime import timedelta
    upcoming = Invoice.objects.filter(
        status='pending',
        due_date=timezone.now().date() + timedelta(days=3)
    ).select_related('customer')
    for inv in upcoming:
        msg = (f"প্রিয় {inv.customer.full_name}, আপনার ইনভয়েস "
               f"{inv.invoice_number} এর পরিমাণ ৳{inv.total} "
               f"তারিখ {inv.due_date} এর মধ্যে পরিশোধ করুন।")
        send_sms_notification.delay(str(inv.customer.id), msg)
    return {'sent': upcoming.count()}


@shared_task(queue='notifications')
def send_invoice_reminder(invoice_id):
    from apps.billing.models import Invoice
    try:
        inv = Invoice.objects.select_related('customer').get(id=invoice_id)
        msg = (f"প্রিয় {inv.customer.full_name}, ইনভয়েস "
               f"{inv.invoice_number} বাকি আছে ৳{inv.balance_due}।")
        send_sms_notification.delay(str(inv.customer.id), msg)
    except Exception as e:
        logger.error(f"Invoice reminder failed: {e}")


@shared_task(queue='notifications')
def send_expiry_reminder(customer_id):
    from apps.customers.models import Customer
    try:
        c = Customer.objects.get(id=customer_id)
        msg = (f"প্রিয় {c.full_name}, আপনার ইন্টারনেট সংযোগের "
               f"মেয়াদ {c.expiry_date} তারিখে শেষ হবে। নবায়ন করুন।")
        send_sms_notification.delay(str(c.id), msg)
    except Exception as e:
        logger.error(f"Expiry reminder failed: {e}")
