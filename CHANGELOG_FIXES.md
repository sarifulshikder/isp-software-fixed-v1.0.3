# ISP Software — Bug Fix Changelog (v1.0.1)

This document lists every fix applied to the original `isp-software-complete.zip`.
Apply these changes by replacing the affected files with the ones in this archive.

## 🔴 Critical fixes

| # | File | Fix |
|---|------|-----|
| 1 | `backend/config/settings/production.py` | `DEBUG = env.bool('DEBUG', default=False)` so `DEBUG=False` in `.env` is actually parsed as a boolean. |
| 2 | `backend/config/__init__.py` | Now imports `celery_app` so `@shared_task` discovery works. |
| 3 | `backend/config/celery.py` | Added scheduled `flush_expired_tokens` task. The orphan `cleanup_old_logs` reference now points to a real implementation. |
| 4 | `backend/utils/tasks.py` (NEW) | Implemented `cleanup_old_logs` and `flush_expired_tokens` so Celery Beat doesn't crash. |
| 5 | `backend/apps/customers/views.py` | Replaced `timezone.timedelta(...)` with `from datetime import timedelta`. `/customers/stats/` no longer 500s. |
| 6 | `backend/Dockerfile` | Replaced `gunicorn` (WSGI) with `daphne` (ASGI) so Django Channels / WebSockets actually work. |
| 7 | `backend/apps/inventory/views.py` | Imported `F` from `django.db.models` so `low_stock` & `summary` no longer raise `NameError`. |
| 8 | `backend/apps/inventory/models.py` | Removed duplicate `Reseller`, `Department`, `StaffProfile`, `Attendance`, `LeaveRequest` models that conflicted with `apps.reseller` and `apps.hr`. |
| 9 | `nginx/ssl/README.md` (NEW) | Documentation + folder placeholder so the Nginx volume mount no longer fails on a missing path. |
| 10 | `nginx/conf.d/.gitkeep` (NEW) | Folder placeholder for the Nginx `conf.d` mount. |
| 11 | `radius/config/clients.conf` (NEW), `radius/Dockerfile`, `docker-compose.yml` | Stopped bind-mounting the entire `/etc/raddb` directory (which used to wipe FreeRADIUS defaults). Only specific overlay files are mounted now. Health-check changed to `radiusd -XC` self-test. |
| 12 | `backend/config/settings/production.py` | Removed `'rest_framework_simplejwt'` from `INSTALLED_APPS` (it is a library, not a Django app). Kept the `token_blacklist` sub-app. |

## 🟠 High priority

| # | File | Fix |
|---|------|-----|
| 13 | `backend/config/settings/production.py` | `ALLOWED_HOSTS` now defaults to `['localhost', '127.0.0.1']` instead of `['*']`. |
| 14 | `backend/apps/accounts/permissions.py` (NEW) | Added role-based permission classes: `IsSuperAdmin`, `IsAdminRole`, `IsManager`, `IsBilling`, `IsTechnician`, `IsSupportStaff`, `IsStaffReadOnlyOrAdminWrite`. Apply them on viewsets where stricter access is needed. |
| 15 | `backend/apps/accounts/serializers.py` | Added `CustomTokenObtainPairSerializer` that embeds `role`, `email`, `full_name`, `is_staff`, `is_superuser` claims into JWTs and returns a `user` object in the login response. |
| 16 | `backend/config/settings/production.py` | Wired `SIMPLE_JWT['TOKEN_OBTAIN_SERIALIZER']` to the new serializer. |
| 17 | `frontend/src/store/authStore.js` | Replaced naive `atob(...)` JWT decoder with a unicode + base64url-safe decoder. Login now uses the backend-provided `user` object first, with JWT claims as fallback. |
| 18 | `backend/apps/customers/models.py` | Customer ID generation now runs inside `transaction.atomic()` + `select_for_update()`, eliminating duplicate-ID races under concurrency. |
| 19 | `backend/apps/billing/tasks.py` | `auto_suspend_customers` now respects `GRACE_PERIOD_DAYS` and only suspends customers whose overdue invoice has actually passed the grace window. |
| 20 | `backend/apps/inventory/serializers.py` | Stock movements are now atomic (`transaction.atomic` + `F()` expressions), preventing lost updates and negative stock under concurrent writes. Quantity is validated > 0. |
| 21 | `docker-compose.yml` | Removed obsolete `version: "3.9"`. Removed `./backend:/app` bind-mount from backend & celery services (it broke the non-root container chown). Persistent paths (`/app/staticfiles`, `/app/media`, `/app/logs`) use named volumes only. |

## 🟡 Medium / housekeeping

| # | File | Fix |
|---|------|-----|
| 22 | `frontend/src/services/api.js` | Refresh logic now: uses configured `baseURL`, deduplicates concurrent refresh attempts, properly redirects to `/login` only when refresh token is missing/invalid. |
| 23 | `frontend/tailwind.config.js`, `frontend/postcss.config.js`, `frontend/src/index.css`, `frontend/src/main.jsx` (NEW) | Added Tailwind/PostCSS configuration that was missing. Frontend now actually compiles CSS. |
| 24 | `frontend/Dockerfile` | Removed reference to non-existent `nginx.conf`. Frontend container now publishes the build output to the shared volume and idles, while the main `nginx` service serves the files. |
| 25 | `nginx/nginx.conf` | Tightened the Content-Security-Policy header (no more wildcard `http:`/`https:`). Made the `/api/v1/auth/` block consistent with `/api/` (timeouts, `proxy_http_version 1.1`, `Connection ""`). |
| 26 | `backend/apps/inventory/views.py` | `summary.total_value` now multiplies `unit_cost * stock_quantity`. `low_stock` correctly filters by `min_stock` (was hard-coded to ≤ 1). |

## ⚠️ Manual follow-up still recommended

These changes are out of scope for an auto-fix and should be planned by the
team:

1. **Add unit / integration tests** — every app currently ships with an empty
   `tests.py`. Without them you have no regression safety net.
2. **Replace `socket.io-client`** in the frontend with the native `WebSocket`
   API, since the backend uses Django Channels (raw WS) — they are not
   protocol-compatible. Or, add `python-socketio` on the backend.
3. **Apply role-based permissions** on each ViewSet using the new classes in
   `apps.accounts.permissions` (the file ships with all the classes ready,
   but you still need to set `permission_classes = [IsBilling]` etc. per
   viewset to your taste).
4. **Pin transitive dependencies** with `pip-compile` so production builds
   are reproducible.
5. **Configure Sentry** (the `sentry-sdk` package is already installed) —
   add `sentry_sdk.init(dsn=env('SENTRY_DSN'))` near the bottom of
   `production.py` once you have a DSN.
6. **Provision SSL certificates** (see `nginx/ssl/README.md`).

---

Original review report and full bug list are preserved in the chat history.
This patch addresses every Critical and High item, and most Medium items.

---

## 🚀 New: `deploy.sh`

Added a one-shot VPS deployment helper that:

1. Checks `docker` and `docker compose` are installed.
2. Generates a hardened `.env` (random `SECRET_KEY`, DB / Redis / RADIUS /
   Flower / pgAdmin passwords) - or keeps an existing `.env` untouched.
3. Creates a self-signed certificate in `nginx/ssl/` if no cert is present.
4. Builds + starts the full stack (`docker compose up -d --build`).
5. Waits for Postgres, then runs `migrate` + `collectstatic`.
6. Interactively creates a Django superuser (skips if one already exists).
7. Prints a summary with all useful URLs and follow-up commands.

Usage:

```bash
chmod +x deploy.sh
./deploy.sh              # interactive
./deploy.sh -y           # non-interactive (CI / re-runs)
```

The script is idempotent - re-running it is safe. It will not overwrite an
existing `.env` or SSL cert.

---

## 🚀 v1.0.2 follow-up (this update)

| # | Item | Detail |
|---|------|--------|
| 1 | `deploy.sh` | Now runs `makemigrations` (per app) before `migrate`, so first deploy creates the database schema correctly. Idempotent on subsequent runs. |
| 2 | `apps/network/consumers.py` (NEW) + `routing.py` | Real WebSocket consumer at `ws/network/alerts/`. Authenticated users join the `network_alerts` group; backend can `group_send` to push live alerts. |
| 3 | `apps/support/consumers.py` (NEW) + `routing.py` | WebSocket at `ws/support/tickets/`. Per-user group `support_<id>` plus a shared `support_staff` group for managers/agents. |
| 4 | `apps/notifications/consumers.py` (NEW) + `routing.py` | WebSocket at `ws/notifications/`. Per-user group `notifications_<id>`. |
| 5 | `config/settings/production.py` | Optional Sentry init (Django + Celery + Redis integrations). Activates only when `SENTRY_DSN` is set. |
| 6 | `.env.example` | Added `SENTRY_DSN`, `SENTRY_ENVIRONMENT`, `SENTRY_TRACES_SAMPLE_RATE`, `APP_VERSION` placeholders. |

WebSocket clients (frontend) should connect with the JWT in the
`Sec-WebSocket-Protocol` header or as a `?token=...` query param and use
the **native `WebSocket` API** (not `socket.io-client`).

---

## 🎯 v1.0.3 — Demo data seeder

Added `apps/customers/management/commands/seed_demo_data.py`. Run it after
`migrate` to populate the database so dashboards and reports look real:

```bash
docker compose exec backend python manage.py seed_demo_data
docker compose exec backend python manage.py seed_demo_data --customers 100
docker compose exec backend python manage.py seed_demo_data --reset    # wipe + reseed
```

What it creates:

- **3 zones** (Demo Zone - Dhaka North / South / Gazipur)
- **5 packages** (Home Basic 5M up to Business 100M, BDT 500-5000)
- **50 customers** (configurable) with realistic Bengali names, phones,
  addresses, status mix (active / suspended / pending / terminated),
  PPPoE credentials, IP addresses, and the tag `"demo"` so they can be
  recognised or removed later.
- **2-4 invoices per customer** with mixed statuses (paid / pending /
  overdue / partial), tax, late fees, and matching invoice items.
- **Payments** for paid + partial invoices (cash / bKash / Nagad / bank).
- **~12-15 support tickets** with mixed categories, priorities, statuses,
  SLA deadlines, and CSAT scores.

`deploy.sh` now asks (interactively) whether to run the seeder right after
`migrate`, so a fresh install can show meaningful data immediately.

The seeder is **safe to re-run**: real customers are never touched (only
those tagged `"demo"` are deleted by `--reset`).
