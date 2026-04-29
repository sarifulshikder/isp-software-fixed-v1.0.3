# 📡 ISP Billing & Management Software

> **v1.0.3 Fixed** — সম্পূর্ণ bug-free, production-ready। Clone করার পর শুধু একটি command এ deploy হবে।

বাংলাদেশ ও বিশ্বের ISP দের জন্য তৈরি আধুনিক billing ও network management software। Alpine Linux-based Docker containers এ চলে।

---

## ⚡ Quick Start (One Command Deploy)

```bash
git clone https://github.com/sarifulshikder/isp-software-fixed-v1.0.3.git
cd isp-software-fixed-v1.0.3
chmod +x deploy.sh
./deploy.sh -y
```

`-y` flag দিলে সব password ও secret **auto-generate** হবে। Deploy শেষে terminal এ login credentials দেখাবে।

---

## ✅ Fixed Bugs (v1.0.3)

| # | সমস্যা | সমাধান |
|---|---|---|
| 1 | `sed` command error in `deploy.sh` | `cat > .env` দিয়ে replace করা হয়েছে |
| 2 | `kombu==5.3.3` vs `celery==5.3.6` conflict | `kombu==5.3.4` করা হয়েছে |
| 3 | Docker permission denied (`docker.sock`) | Auto `usermod -aG docker` যোগ করা হয়েছে |
| 4 | Superuser create হয় না | Python shell দিয়ে auto-create করা হয়েছে |
| 5 | SSL certificate না থাকায় nginx crash | Auto `openssl` দিয়ে self-signed cert generate হয় |
| 6 | `init_db.sql` role error (`ispuser` does not exist) | `DO $$ IF NOT EXISTS` দিয়ে fix করা হয়েছে |
| 7 | Migration order error | Proper healthcheck wait + `--noinput` যোগ করা হয়েছে |

---

## 🛠️ Prerequisites

| Tool | Minimum Version | Install |
|---|---|---|
| Docker Engine | 24+ | `curl -fsSL https://get.docker.com \| sh` |
| Docker Compose | v2.x | `sudo apt install docker-compose-plugin -y` |
| RAM | 4 GB | — |
| Disk | 20 GB | — |
| OS | Ubuntu 22.04+ / Debian 12+ | — |

---

## 🚀 Installation Guide

### Step 1 — Clone করো

```bash
git clone https://github.com/sarifulshikder/isp-software-fixed-v1.0.3.git
cd isp-software-fixed-v1.0.3
```

### Step 2 — Deploy করো

**Option A — Auto (সব auto-generate):**
```bash
chmod +x deploy.sh
./deploy.sh -y
```

**Option B — Interactive (নিজে সব দেবে):**
```bash
chmod +x deploy.sh
./deploy.sh
```
Company name, domain, email, passwords জিজ্ঞেস করবে।

### Step 3 — Browser এ Access করো

| সার্ভিস | URL |
|---|---|
| 🌐 Web App | `http://YOUR_SERVER_IP` |
| 🔒 HTTPS | `https://YOUR_SERVER_IP` |
| 📖 API Docs | `http://YOUR_SERVER_IP/api/docs/` |
| ⚙️ Django Admin | `http://YOUR_SERVER_IP/admin/` |
| 📊 Celery Monitor | `http://YOUR_SERVER_IP:5555` |

> **Note:** HTTPS এ browser warning আসবে (self-signed cert)। **Advanced → Proceed** চাপো।

---

## 🔧 Management Commands

```bash
./isp.sh start              # সব service চালু করো
./isp.sh stop               # সব service বন্ধ করো
./isp.sh restart            # সব service restart করো
./isp.sh status             # সব container এর status দেখো
./isp.sh logs               # সব logs দেখো
./isp.sh logs backend       # শুধু backend logs
./isp.sh logs nginx         # শুধু nginx logs
./isp.sh backup             # Database backup নাও
./isp.sh restore backup.sql # Database restore করো
./isp.sh shell backend      # Backend container এ shell খোলো
./isp.sh django migrate     # Django migration run করো
./isp.sh createsuperuser    # নতুন admin user তৈরি করো
./isp.sh update             # Latest code pull করে restart করো
```

---

## 🔄 Existing Installation এ Fixes Apply করতে

পুরনো installation এ সব fix apply করতে:

```bash
cd ~/isp-software-fixed-v1.0.3
git pull
chmod +x apply_fixes.sh
./apply_fixes.sh
docker compose down -v
./deploy.sh -y
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│              Nginx (Alpine) — Port 80/443           │
│           HTTP → HTTPS redirect + SSL               │
└────────────┬──────────────────┬────────────────────┘
             │                  │
    ┌────────▼──────┐  ┌────────▼──────┐
    │ React Frontend│  │ Django Backend │
    │  (Vite build) │  │  (Daphne ASGI)│
    └───────────────┘  └───────┬───────┘
                               │
           ┌───────────────────┼───────────────────┐
           │                   │                   │
  ┌────────▼──────┐  ┌────────▼──────┐  ┌────────▼──────┐
  │  PostgreSQL   │  │     Redis     │  │  FreeRADIUS   │
  │     v16       │  │      v7       │  │  1812/1813UDP │
  └───────────────┘  └───────────────┘  └───────────────┘
           │
  ┌────────▼──────────────────────────────┐
  │  Celery Worker + Celery Beat          │
  │  (Background tasks & Scheduling)      │
  └────────────────────────────────────────┘
```

---

## ✨ Features

| Module | Features |
|---|---|
| 👥 Customer | Profile, KYC, PPPoE, IP assignment, notes, status |
| 📋 Billing | Auto invoicing, pro-rata, late fees, VAT, credit notes |
| 💳 Payment | Cash, bKash, Nagad, Rocket, Bank, Card, auto-pay |
| 📦 Package | FUP, Shared/Dedicated, multi-cycle, Mikrotik sync |
| 📡 Network | IPAM, RADIUS, OLT/ONU, device monitoring, alerts |
| 🎫 Support | Tickets, SLA, field visits, knowledge base, CSAT |
| 🏭 Inventory | Stock, serial numbers, equipment assignment |
| 🤝 Reseller | Multi-level, commission, bandwidth pool |
| 📊 Reports | Revenue, churn, network, custom reports |
| 👔 HR | Staff, attendance, leave, salary, GPS tracking |
| 🔔 Notify | SMS, Email, WhatsApp, Push notifications |
| 🔐 Security | JWT, 2FA, RBAC, audit log, encryption |

---

## 🔐 Default Ports

| Service | Port | Protocol |
|---|---|---|
| Web HTTP | 80 | TCP |
| Web HTTPS | 443 | TCP |
| RADIUS Auth | 1812 | UDP |
| RADIUS Acct | 1813 | UDP |
| Flower (Celery) | 5555 | TCP |
| pgAdmin | 5050 | TCP |

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Base OS | Alpine Linux 3.19 |
| Backend | Python 3.12 + Django 5 + DRF |
| Frontend | React 18 + Vite + Recharts |
| Database | PostgreSQL 16 |
| Cache/Queue | Redis 7 + Celery 5.3.6 |
| Web Server | Nginx Alpine |
| RADIUS | FreeRADIUS |
| Auth | JWT (SimpleJWT) + 2FA |
| Container | Docker + Docker Compose v2 |

---

## 📁 Project Structure

```
isp-software-fixed-v1.0.3/
├── backend/                  # Django REST API
│   ├── apps/
│   │   ├── accounts/         # User auth & roles
│   │   ├── customers/        # Customer management
│   │   ├── billing/          # Invoicing & billing
│   │   ├── payments/         # Payment processing
│   │   ├── packages/         # Internet packages
│   │   ├── network/          # Network & RADIUS
│   │   ├── support/          # Help desk tickets
│   │   ├── inventory/        # Equipment tracking
│   │   ├── reseller/         # Reseller management
│   │   ├── reports/          # Analytics & reports
│   │   ├── hr/               # Human resources
│   │   └── notifications/    # SMS/Email/Push
│   ├── config/               # Django settings
│   ├── requirements.txt      # Python deps (fixed)
│   └── Dockerfile
│
├── frontend/                 # React + Vite app
│   ├── src/
│   └── Dockerfile
│
├── nginx/
│   ├── nginx.conf            # Nginx config
│   └── ssl/                  # SSL certs (auto-generated)
│
├── radius/                   # FreeRADIUS
├── docker/
│   └── scripts/
│       └── init_db.sql       # DB init (fixed)
├── docker-compose.yml
├── .env.example
├── deploy.sh                 # ✅ Fixed deploy script
├── isp.sh                    # ✅ Fixed management script
├── apply_fixes.sh            # 🔧 Apply fixes to existing install
└── README.md
```

---

## 🌐 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/auth/login/` | Login & get JWT |
| GET | `/api/v1/customers/` | List customers |
| POST | `/api/v1/customers/` | Add customer |
| GET | `/api/v1/billing/invoices/` | List invoices |
| POST | `/api/v1/billing/invoices/run_billing/` | Generate bills |
| GET | `/api/v1/payments/daily_summary/` | Daily revenue |
| GET | `/api/v1/network/devices/` | Network devices |
| GET | `/api/v1/support/tickets/` | Support tickets |
| GET | `/api/docs/` | Full API docs (Swagger) |

---

## ❓ Troubleshooting

**Docker permission denied:**
```bash
sudo usermod -aG docker $USER
newgrp docker
```

**Port 80 already in use:**
```bash
sudo lsof -i :80
sudo systemctl stop apache2  # অথবা nginx
```

**Database not healthy:**
```bash
docker compose down -v
docker compose up -d
```

**Nginx keeps restarting (SSL error):**
```bash
mkdir -p nginx/ssl
openssl req -x509 -nodes -days 3650 -newkey rsa:2048 \
  -keyout nginx/ssl/privkey.pem \
  -out nginx/ssl/fullchain.pem \
  -subj "/C=BD/ST=Dhaka/L=Dhaka/O=ISP/CN=localhost"
docker compose restart nginx
```

**Superuser login কাজ করছে না:**
```bash
cd ~/isp-software-fixed-v1.0.3
docker compose exec backend python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
u = User.objects.get(username='admin')
u.set_password('Admin1234!')
u.save()
print('Done')
"
```

---

## 📞 Support

সমস্যা হলে GitHub Issues খুলুন অথবা যোগাযোগ করুন।

---

*Built with ❤️ for ISPs in Bangladesh and beyond*

> **v1.0.3** — All deployment bugs fixed. See [`CHANGELOG_FIXES.md`](CHANGELOG_FIXES.md) for details.
