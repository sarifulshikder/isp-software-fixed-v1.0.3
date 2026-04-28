"""
Seed demo data so the dashboards aren't empty on a fresh install.

Usage (after `migrate`):

    docker compose exec backend python manage.py seed_demo_data
    docker compose exec backend python manage.py seed_demo_data --customers 100
    docker compose exec backend python manage.py seed_demo_data --reset

`--reset` deletes existing demo rows (those tagged "demo") before seeding,
so you can re-run safely. Real customers (without the "demo" tag) are
never touched.
"""
import random
from decimal import Decimal
from datetime import timedelta, datetime, time

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from apps.customers.models import Customer, Zone
from apps.packages.models import Package
from apps.billing.models import Invoice, InvoiceItem
from apps.payments.models import Payment
from apps.support.models import Ticket

User = get_user_model()

FIRST_NAMES = [
    'Rahim', 'Karim', 'Salma', 'Nusrat', 'Tanvir', 'Sumon', 'Mehedi', 'Arif',
    'Sabbir', 'Jahid', 'Faruk', 'Rashed', 'Mahmud', 'Imran', 'Shahed', 'Asif',
    'Tahmid', 'Rakib', 'Nayeem', 'Habib', 'Mou', 'Tania', 'Rumi', 'Sadia',
    'Lamia', 'Munira', 'Sharmin', 'Tanjila', 'Farzana', 'Ayesha',
]
LAST_NAMES = [
    'Hossain', 'Rahman', 'Ahmed', 'Khan', 'Islam', 'Akter', 'Begum', 'Sultana',
    'Hasan', 'Karim', 'Chowdhury', 'Mia', 'Uddin', 'Mahmud', 'Siddique',
]
AREAS = ['Dhanmondi', 'Gulshan', 'Mirpur', 'Uttara', 'Mohammadpur', 'Banani',
         'Bashundhara', 'Tejgaon', 'Khilgaon', 'Motijheel']
TICKET_SUBJECTS = [
    ('no_internet', 'Internet completely down since morning'),
    ('slow_speed', 'Speed much slower than my package'),
    ('billing', 'Last month invoice double-charged'),
    ('billing', 'Need invoice copy for tax filing'),
    ('upgrade', 'Want to upgrade to a higher package'),
    ('relocation', 'Moving to new address - need to relocate connection'),
    ('device_issue', 'Router LED is red - device may be faulty'),
    ('installation', 'Requesting new fiber installation at office'),
]


def random_phone():
    return f"+8801{random.randint(3,9)}{random.randint(10000000, 99999999)}"


class Command(BaseCommand):
    help = 'Seed the database with demo customers, invoices, payments, tickets.'

    def add_arguments(self, parser):
        parser.add_argument('--customers', type=int, default=50,
                            help='Number of demo customers to create (default: 50).')
        parser.add_argument('--reset', action='store_true',
                            help='Delete existing demo data before seeding.')

    @transaction.atomic
    def handle(self, *args, **opts):
        n_customers = opts['customers']
        do_reset = opts['reset']

        if do_reset:
            self._reset()

        self.stdout.write(self.style.NOTICE('Seeding zones...'))
        zones = self._seed_zones()

        self.stdout.write(self.style.NOTICE('Seeding packages...'))
        packages = self._seed_packages()

        self.stdout.write(self.style.NOTICE(f'Seeding {n_customers} customers...'))
        customers = self._seed_customers(n_customers, zones, packages)

        self.stdout.write(self.style.NOTICE('Seeding invoices and payments...'))
        n_invoices, n_payments = self._seed_billing(customers)

        self.stdout.write(self.style.NOTICE('Seeding support tickets...'))
        n_tickets = self._seed_tickets(customers)

        self.stdout.write(self.style.SUCCESS(
            f'\nDone. Created: {len(zones)} zones, {len(packages)} packages, '
            f'{len(customers)} customers, {n_invoices} invoices, {n_payments} payments, '
            f'{n_tickets} tickets.'
        ))
        self.stdout.write(self.style.WARNING(
            'All demo customers have the tag "demo" so you can identify or remove them later.'
        ))

    # ── Reset ──────────────────────────────────────────────
    def _reset(self):
        self.stdout.write(self.style.WARNING('Removing existing demo rows...'))
        demo_customers = Customer.objects.filter(tags__contains=['demo'])
        Ticket.objects.filter(customer__in=demo_customers).delete()
        Payment.objects.filter(customer__in=demo_customers).delete()
        InvoiceItem.objects.filter(invoice__customer__in=demo_customers).delete()
        Invoice.objects.filter(customer__in=demo_customers).delete()
        deleted = demo_customers.count()
        demo_customers.delete()
        Package.objects.filter(code__startswith='DEMO').delete()
        Zone.objects.filter(name__startswith='Demo Zone').delete()
        self.stdout.write(self.style.WARNING(f'Removed {deleted} demo customers + linked rows.'))

    # ── Zones ──────────────────────────────────────────────
    def _seed_zones(self):
        names = ['Demo Zone - Dhaka North', 'Demo Zone - Dhaka South', 'Demo Zone - Gazipur']
        zones = []
        for name in names:
            z, _ = Zone.objects.get_or_create(name=name, defaults={
                'description': 'Auto-seeded demo zone',
                'is_active': True,
            })
            zones.append(z)
        return zones

    # ── Packages ───────────────────────────────────────────
    def _seed_packages(self):
        defs = [
            ('DEMO-5M',   'Home Basic 5Mbps',     'fiber',  5_000,   2_500,  Decimal('500')),
            ('DEMO-10M',  'Home Standard 10Mbps', 'fiber', 10_000,   5_000,  Decimal('800')),
            ('DEMO-20M',  'Home Plus 20Mbps',     'fiber', 20_000,  10_000,  Decimal('1200')),
            ('DEMO-50M',  'Pro 50Mbps',           'fiber', 50_000,  25_000,  Decimal('2500')),
            ('DEMO-100M', 'Business 100Mbps',     'fiber', 100_000, 50_000,  Decimal('5000')),
        ]
        packages = []
        for code, name, _, dl, ul, price in defs:
            p, _ = Package.objects.get_or_create(code=code, defaults={
                'name': name,
                'description': 'Auto-seeded demo package',
                'download_speed': dl,
                'upload_speed': ul,
                'price': price,
                'billing_cycle': 'monthly',
                'is_active': True,
                'is_public': True,
            })
            packages.append(p)
        return packages

    # ── Customers ──────────────────────────────────────────
    def _seed_customers(self, n, zones, packages):
        statuses = (['active'] * 70) + (['suspended'] * 15) + (['pending'] * 10) + (['terminated'] * 5)
        connection_types = ['fiber', 'fiber', 'fiber', 'cable', 'wireless']
        today = timezone.now().date()
        customers = []

        for i in range(n):
            first = random.choice(FIRST_NAMES)
            last = random.choice(LAST_NAMES)
            connect_date = today - timedelta(days=random.randint(30, 720))
            status = random.choice(statuses)
            expiry = today + timedelta(days=random.randint(-15, 30))

            c = Customer.objects.create(
                first_name=first,
                last_name=last,
                email=f'{first.lower()}.{last.lower()}{i}@demo.local',
                phone=random_phone(),
                nid_number=str(random.randint(1_000_000_000, 9_999_999_999)),
                address=f'{random.randint(1, 999)}/{random.choice(["A","B","C"])}, '
                        f'{random.choice(AREAS)}',
                area=random.choice(AREAS),
                city='Dhaka',
                zone=random.choice(zones),
                connection_type=random.choice(connection_types),
                package=random.choice(packages),
                status=status,
                billing_day=random.randint(1, 28),
                installation_fee=Decimal(random.choice([0, 500, 1000])),
                installation_paid=random.choice([True, True, False]),
                connection_date=connect_date,
                expiry_date=expiry,
                ip_address=f'10.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(2,254)}',
                pppoe_username=f'demo{i:04d}',
                pppoe_password=f'pwd{random.randint(10000,99999)}',
                tags=['demo'],
            )
            customers.append(c)
        return customers

    # ── Billing + Payments ─────────────────────────────────
    def _seed_billing(self, customers):
        invoice_count = 0
        payment_count = 0
        today = timezone.now().date()

        for c in customers:
            n_invoices = random.randint(2, 4)
            for k in range(n_invoices):
                months_ago = n_invoices - k
                start = (today.replace(day=1) - timedelta(days=30 * months_ago)).replace(day=1)
                end = (start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
                due = end + timedelta(days=7)

                # Status logic: older invoices likely paid, latest may be pending/overdue.
                if k == n_invoices - 1:
                    status = random.choices(
                        ['paid', 'pending', 'overdue', 'partial'],
                        weights=[40, 30, 20, 10],
                    )[0]
                else:
                    status = random.choices(['paid', 'overdue'], weights=[85, 15])[0]

                subtotal = c.package.price
                tax = subtotal * Decimal('0.05')
                late_fee = Decimal('50') if status == 'overdue' else Decimal('0')
                total = subtotal + tax + late_fee
                amount_paid = (
                    total if status == 'paid'
                    else (total / 2 if status == 'partial' else Decimal('0'))
                )

                inv = Invoice.objects.create(
                    customer=c,
                    invoice_type='monthly',
                    status=status,
                    subtotal=subtotal,
                    tax_amount=tax,
                    late_fee=late_fee,
                    total=total,
                    amount_paid=amount_paid,
                    balance_due=total - amount_paid,
                    billing_period_start=start,
                    billing_period_end=end,
                    due_date=due,
                    paid_date=due - timedelta(days=random.randint(0, 5)) if status == 'paid' else None,
                    package_name=c.package.name,
                    package_price=c.package.price,
                )
                InvoiceItem.objects.create(
                    invoice=inv,
                    description=f'Internet service - {c.package.name} ({start} to {end})',
                    quantity=Decimal('1'),
                    unit_price=subtotal,
                    total=subtotal,
                )
                invoice_count += 1

                if amount_paid > 0:
                    pay_dt = datetime.combine(
                        due - timedelta(days=random.randint(0, 5)), time(12, 0)
                    )
                    pay_dt = timezone.make_aware(pay_dt) if timezone.is_naive(pay_dt) else pay_dt
                    Payment.objects.create(
                        customer=c,
                        invoice=inv,
                        method=random.choice(['cash', 'bkash', 'nagad', 'bank']),
                        status='completed',
                        amount=amount_paid,
                        payment_date=pay_dt,
                        reference=f'DEMO-{random.randint(100000,999999)}',
                    )
                    payment_count += 1

        return invoice_count, payment_count

    # ── Tickets ────────────────────────────────────────────
    def _seed_tickets(self, customers):
        n_tickets = max(10, len(customers) // 4)
        sample = random.sample(customers, min(n_tickets, len(customers)))
        priorities = ['low', 'medium', 'medium', 'high', 'critical']
        statuses = ['open', 'in_progress', 'in_progress', 'resolved', 'resolved', 'closed']
        now = timezone.now()
        count = 0
        for c in sample:
            cat, subject = random.choice(TICKET_SUBJECTS)
            status = random.choice(statuses)
            created = now - timedelta(days=random.randint(0, 30), hours=random.randint(0, 23))
            sla_hours = random.choice([4, 8, 24, 48])
            t = Ticket.objects.create(
                customer=c,
                category=cat,
                priority=random.choice(priorities),
                status=status,
                subject=subject,
                description=f'{subject}. Customer: {c.full_name}. Reported via demo seeder.',
                sla_hours=sla_hours,
                sla_deadline=created + timedelta(hours=sla_hours),
                resolution='Issue resolved by field tech.' if status in ('resolved', 'closed') else '',
                resolved_at=created + timedelta(hours=random.randint(1, sla_hours))
                            if status in ('resolved', 'closed') else None,
                csat_score=random.randint(3, 5) if status in ('resolved', 'closed') else None,
            )
            t.created_at = created
            t.save(update_fields=['created_at'])
            count += 1
        return count
