"""
ISP Software - Billing Automation Tasks
"""
from celery import shared_task
from celery.utils.log import get_task_logger
from django.utils import timezone
from django.db import transaction
from datetime import timedelta
import logging

logger = get_task_logger(__name__)


@shared_task(queue='billing', bind=True, max_retries=3)
def generate_monthly_invoices(self):
    """Generate invoices for all active customers on billing day"""
    from apps.customers.models import Customer
    from apps.billing.models import Invoice, InvoiceItem

    today = timezone.now().date()
    generated = 0
    errors = 0

    customers = Customer.objects.filter(
        status='active',
        billing_day=today.day
    ).select_related('package')

    for customer in customers:
        try:
            with transaction.atomic():
                # Check if invoice already exists for this period
                existing = Invoice.objects.filter(
                    customer=customer,
                    billing_period_start__year=today.year,
                    billing_period_start__month=today.month,
                    invoice_type='monthly',
                ).exists()

                if existing:
                    continue

                period_start = today
                period_end = (today.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)
                due_date = today + timedelta(days=7)

                invoice = Invoice.objects.create(
                    customer=customer,
                    invoice_type='monthly',
                    status='pending',
                    subtotal=customer.package.price,
                    discount=0,
                    tax_amount=0,
                    late_fee=0,
                    total=customer.package.price,
                    amount_paid=0,
                    balance_due=customer.package.price,
                    billing_period_start=period_start,
                    billing_period_end=period_end,
                    due_date=due_date,
                    package_name=customer.package.name,
                    package_price=customer.package.price,
                )

                InvoiceItem.objects.create(
                    invoice=invoice,
                    description=f"{customer.package.name} - {period_start} to {period_end}",
                    quantity=1,
                    unit_price=customer.package.price,
                    total=customer.package.price,
                )

                generated += 1
                logger.info(f"Invoice generated for customer {customer.customer_id}")

        except Exception as exc:
            errors += 1
            logger.error(f"Error generating invoice for {customer.customer_id}: {exc}")

    logger.info(f"Invoice generation complete: {generated} generated, {errors} errors")
    return {'generated': generated, 'errors': errors}


@shared_task(queue='billing', bind=True)
def apply_late_fees(self):
    """Apply late fees to overdue invoices"""
    from apps.billing.models import Invoice
    from django.conf import settings

    today = timezone.now().date()
    grace_days = settings.ISP_SETTINGS.get('GRACE_PERIOD_DAYS', 7)
    late_fee_rate = settings.ISP_SETTINGS.get('LATE_FEE_RATE', 2.0)
    overdue_date = today - timedelta(days=grace_days)

    invoices = Invoice.objects.filter(
        status='pending',
        due_date__lte=overdue_date,
        late_fee=0,
    )

    updated = 0
    for invoice in invoices:
        fee = (invoice.subtotal * late_fee_rate) / 100
        invoice.late_fee = fee
        invoice.total = invoice.subtotal + invoice.tax_amount + fee - invoice.discount
        invoice.balance_due = invoice.total - invoice.amount_paid
        invoice.status = 'overdue'
        invoice.save()
        updated += 1

    logger.info(f"Late fees applied to {updated} invoices")
    return {'updated': updated}


@shared_task(queue='billing')
def auto_suspend_customers():
    """Suspend customers with overdue invoices past grace period"""
    from apps.customers.models import Customer
    from apps.billing.models import Invoice
    from apps.network.tasks import suspend_customer_radius
    from django.conf import settings

    today = timezone.now().date()
    grace_days = settings.ISP_SETTINGS.get('GRACE_PERIOD_DAYS', 7)
    cutoff_date = today - timedelta(days=grace_days)
    suspended = 0

    # Only suspend customers whose overdue invoice has passed the grace period
    overdue_customers = Customer.objects.filter(
        status='active',
        invoices__status='overdue',
        invoices__due_date__lte=cutoff_date,
    ).distinct()

    for customer in overdue_customers:
        customer.status = 'suspended'
        customer.suspension_date = today
        customer.save(update_fields=['status', 'suspension_date'])
        try:
            suspend_customer_radius.delay(str(customer.id))
        except Exception as exc:
            logger.error(f"RADIUS suspend dispatch failed for {customer.customer_id}: {exc}")
        suspended += 1
        logger.info(f"Suspended customer {customer.customer_id}")

    return {'suspended': suspended}


@shared_task(queue='billing')
def check_expiring_packages():
    """Alert for packages expiring in next 3 days"""
    from apps.customers.models import Customer
    from apps.notifications.tasks import send_expiry_reminder

    today = timezone.now().date()
    three_days = today + timedelta(days=3)

    expiring = Customer.objects.filter(
        status='active',
        expiry_date__range=[today, three_days]
    )

    for customer in expiring:
        send_expiry_reminder.delay(str(customer.id))

    return {'expiring': expiring.count()}


@shared_task(queue='billing')
def generate_daily_revenue_report():
    """Generate and cache daily revenue summary"""
    from apps.payments.models import Payment
    from django.core.cache import cache

    today = timezone.now().date()
    payments = Payment.objects.filter(
        payment_date__date=today,
        status='completed'
    )

    summary = {
        'date': str(today),
        'total': str(sum(p.amount for p in payments)),
        'count': payments.count(),
        'by_method': {},
    }

    for payment in payments:
        method = payment.method
        if method not in summary['by_method']:
            summary['by_method'][method] = {'count': 0, 'amount': '0'}
        summary['by_method'][method]['count'] += 1
        current = float(summary['by_method'][method]['amount'])
        summary['by_method'][method]['amount'] = str(current + float(payment.amount))

    cache.set('daily_revenue_report', summary, timeout=86400)
    return summary
