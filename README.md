# 📡 ISP Billing & Management Software

একটি সম্পূর্ণ আধুনিক ISP ব্যবস্থাপনা সফটওয়্যার — Alpine Linux-ভিত্তিক Docker Containers-এ।

> **v1.0.1** — সম্পূর্ণ কোড রিভিউ ও বাগ-ফিক্স প্রয়োগ করা হয়েছে। সব পরিবর্তনের তালিকা আছে [`CHANGELOG_FIXES.md`](./CHANGELOG_FIXES.md)-এ।

## ⚡ Quick Start (One-shot deploy)

```bash
chmod +x deploy.sh
./deploy.sh           # interactive: domain, passwords ইত্যাদির prompt দেবে
./deploy.sh -y        # non-interactive: সব secret auto-generate করবে
```

স্ক্রিপ্ট যা করে: docker prerequisites চেক → `.env` জেনারেট (strong random secrets) → self-signed SSL cert বানায় → `docker compose build && up -d` → migrations + collectstatic → Django superuser তৈরি (interactive)।

দৈনন্দিন কন্ট্রোলের জন্য `./isp.sh start|stop|restart|logs|status|backup|update|shell` ব্যবহার করুন।

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                   Nginx (Alpine)                     │
│              Port 80 / 443 (HTTPS)                  │
└────────────┬──────────────────┬────────────────────┘
             │                  │
    ┌────────▼──────┐  ┌────────▼──────┐
    │ React Frontend│  │ Django Backend │
    │  (Port 3000)  │  │  (Port 8000)  │
    └───────────────┘  └───────┬───────┘
                               │
           ┌───────────────────┼───────────────────┐
           │                   │                   │
  ┌────────▼──────┐  ┌────────▼──────┐  ┌────────▼──────┐
  │  PostgreSQL   │  │     Redis     │  │  FreeRADIUS   │
  │  (Port 5432)  │  │  (Port 6379)  │  │(1812/1813 UDP)│
  └───────────────┘  └───────────────┘  └───────────────┘
           │
  ┌────────▼──────────────────────────────┐
  │  Celery Worker + Celery Beat          │
  │  (Background tasks & Scheduling)      │
  └────────────────────────────────────────┘
```

---

## ✅ Features

| Module | Features |
|--------|----------|
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

## 🚀 Quick Start

### Prerequisites
- Docker Engine 24+
- Docker Compose 2.x
- 4GB RAM minimum
- 20GB disk space

### Installation

```bash
# 1. Clone the project
git clone https://github.com/your-org/isp-software.git
cd isp-software

# 2. Setup environment
cp .env.example .env
nano .env   # Edit your settings

# 3. Start everything with one command
chmod +x isp.sh
./isp.sh start

# 4. Create admin user
./isp.sh createsuperuser

# 5. Access the application
# Web App:   http://localhost
# API Docs:  http://localhost/api/docs/
# Admin:     http://localhost/admin/
```

---

## 🔧 Management Commands

```bash
./isp.sh start              # Start all services
./isp.sh stop               # Stop all services
./isp.sh restart            # Restart all services
./isp.sh status             # Check service status
./isp.sh logs               # View all logs
./isp.sh logs backend       # View backend logs only
./isp.sh backup             # Backup database
./isp.sh restore backup.sql # Restore database
./isp.sh shell backend      # Open Django shell
./isp.sh django migrate     # Run Django migrations
./isp.sh update             # Update to latest version
```

---

## 📁 Project Structure

```
isp-software/
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
│   ├── utils/                # Utilities & helpers
│   ├── Dockerfile            # Alpine-based image
│   └── requirements.txt      # Python dependencies
│
├── frontend/                 # React + Vite app
│   ├── src/
│   │   ├── pages/            # All page components
│   │   ├── components/       # Shared UI components
│   │   ├── services/         # API service layer
│   │   ├── store/            # Zustand state management
│   │   └── main.jsx          # App entry point
│   ├── Dockerfile            # Alpine-based build
│   └── package.json
│
├── nginx/                    # Nginx reverse proxy
│   └── nginx.conf
├── radius/                   # FreeRADIUS server
│   ├── Dockerfile
│   └── config/
├── docker/
│   └── scripts/init_db.sql   # Database init
├── docker-compose.yml        # Full stack definition
├── .env.example              # Environment template
├── isp.sh                    # Management script
└── README.md
```

---

## 🌐 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
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

## 🔐 Default Ports

| Service | Port |
|---------|------|
| Web (HTTP) | 80 |
| Web (HTTPS) | 443 |
| RADIUS Auth | 1812/udp |
| RADIUS Acct | 1813/udp |
| Flower (Celery Monitor) | 5555 |
| pgAdmin | 5050 |

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Base OS | **Alpine Linux 3.19** |
| Backend | **Python 3.12 + Django 5 + DRF** |
| Frontend | **React 18 + Vite + Recharts** |
| Database | **PostgreSQL 16** |
| Cache/Queue | **Redis 7 + Celery** |
| Web Server | **Nginx Alpine** |
| RADIUS | **FreeRADIUS** |
| Auth | **JWT (SimpleJWT)** |
| Container | **Docker + Docker Compose** |

---

## 📞 Support

For issues and customization, please open a GitHub issue or contact the development team.

---

*Built with ❤️ for ISPs in Bangladesh and beyond*
