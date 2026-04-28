#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────
# ISP Software - One-shot VPS Deployment Helper
#
# Usage:
#   chmod +x deploy.sh
#   ./deploy.sh                # interactive
#   ./deploy.sh --non-interactive   # use env defaults / .env if present
#
# What it does:
#   1. Verifies docker + docker compose are installed
#   2. Generates a strong .env (or keeps existing one)
#   3. Creates a self-signed SSL cert in nginx/ssl/ if none exists
#   4. Builds and starts the full stack
#   5. Runs migrations + collectstatic
#   6. Creates a Django superuser (interactive)
# ─────────────────────────────────────────────────────────────

set -euo pipefail

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# ── Colors ──────────────────────────────────────────────────
RED='\033[0;31m'; GRN='\033[0;32m'; YLW='\033[1;33m'; BLU='\033[0;34m'; NC='\033[0m'
log()   { printf "${BLU}[deploy]${NC} %s\n" "$*"; }
ok()    { printf "${GRN}[ ok  ]${NC} %s\n" "$*"; }
warn()  { printf "${YLW}[warn]${NC} %s\n" "$*"; }
err()   { printf "${RED}[ err ]${NC} %s\n" "$*" >&2; }

NON_INTERACTIVE=0
for arg in "$@"; do
  case "$arg" in
    --non-interactive|-y) NON_INTERACTIVE=1 ;;
    --help|-h)
      sed -n '2,15p' "$0"; exit 0 ;;
  esac
done

ask() {
  # ask "Prompt" "default" -> echoes user input or default
  local prompt="$1" default="${2:-}" reply=""
  if [[ "$NON_INTERACTIVE" == "1" ]]; then
    echo "$default"; return
  fi
  if [[ -n "$default" ]]; then
    read -r -p "$prompt [$default]: " reply
  else
    read -r -p "$prompt: " reply
  fi
  echo "${reply:-$default}"
}

ask_secret() {
  # ask_secret "Prompt" -> echoes typed (hidden) input or generated 32-byte hex
  local prompt="$1" reply=""
  if [[ "$NON_INTERACTIVE" == "1" ]]; then
    gen_secret; return
  fi
  read -r -s -p "$prompt (leave blank to auto-generate): " reply
  echo
  if [[ -z "$reply" ]]; then
    gen_secret
  else
    echo "$reply"
  fi
}

gen_secret() {
  if command -v openssl >/dev/null 2>&1; then
    openssl rand -hex 24
  else
    head -c 32 /dev/urandom | base64 | tr -d '/+=' | cut -c1-40
  fi
}

# ── 1. Pre-flight checks ───────────────────────────────────
log "Checking prerequisites..."
command -v docker >/dev/null 2>&1 || { err "docker is not installed. Install Docker Engine first."; exit 1; }
if docker compose version >/dev/null 2>&1; then
  COMPOSE="docker compose"
elif command -v docker-compose >/dev/null 2>&1; then
  COMPOSE="docker-compose"
else
  err "docker compose plugin not found. Install docker-compose-plugin."
  exit 1
fi
ok "Docker: $(docker --version)"
ok "Compose: $($COMPOSE version | head -n1)"

# ── 2. .env generation ─────────────────────────────────────
if [[ -f .env ]]; then
  warn ".env already exists - keeping it. Delete it first to regenerate."
else
  log "Generating .env from .env.example..."
  cp .env.example .env

  COMPANY=$(ask "Company name"           "My Internet Service Provider")
  DOMAIN=$(ask  "Primary domain (no http://)"  "isp.example.com")
  ADMIN_EMAIL=$(ask "Admin email"        "admin@${DOMAIN}")

  SECRET_KEY=$(gen_secret)$(gen_secret)
  DB_PASSWORD=$(ask_secret "DB password")
  REDIS_PASSWORD=$(ask_secret "Redis password")
  RADIUS_SECRET=$(ask_secret "RADIUS shared secret")
  FLOWER_PASSWORD=$(ask_secret "Flower (celery monitor) password")
  PGADMIN_PASSWORD=$(ask_secret "pgAdmin password")

  # Cross-platform sed -i
  sedi() {
    if sed --version >/dev/null 2>&1; then sed -i "$@"; else sed -i '' "$@"; fi
  }

  sedi "s|^SECRET_KEY=.*|SECRET_KEY=${SECRET_KEY}|"                           .env
  sedi "s|^DEBUG=.*|DEBUG=False|"                                              .env
  sedi "s|^ALLOWED_HOSTS=.*|ALLOWED_HOSTS=localhost,127.0.0.1,${DOMAIN}|"     .env
  sedi "s|^CORS_ALLOWED_ORIGINS=.*|CORS_ALLOWED_ORIGINS=https://${DOMAIN}|"   .env
  sedi "s|^DB_PASSWORD=.*|DB_PASSWORD=${DB_PASSWORD}|"                         .env
  sedi "s|^REDIS_PASSWORD=.*|REDIS_PASSWORD=${REDIS_PASSWORD}|"                .env
  sedi "s|^COMPANY_NAME=.*|COMPANY_NAME=${COMPANY}|"                           .env
  sedi "s|^COMPANY_EMAIL=.*|COMPANY_EMAIL=${ADMIN_EMAIL}|"                     .env

  # Append values that may not already exist in the example
  grep -q '^RADIUS_SECRET='   .env || echo "RADIUS_SECRET=${RADIUS_SECRET}"     >> .env
  grep -q '^FLOWER_USER='     .env || echo "FLOWER_USER=admin"                  >> .env
  grep -q '^FLOWER_PASSWORD=' .env || echo "FLOWER_PASSWORD=${FLOWER_PASSWORD}" >> .env
  grep -q '^PGADMIN_EMAIL='   .env || echo "PGADMIN_EMAIL=${ADMIN_EMAIL}"       >> .env
  grep -q '^PGADMIN_PASSWORD=' .env || echo "PGADMIN_PASSWORD=${PGADMIN_PASSWORD}" >> .env

  chmod 600 .env
  ok ".env generated (chmod 600)"
fi

# ── 3. SSL certificate ─────────────────────────────────────
mkdir -p nginx/ssl
if [[ -f nginx/ssl/fullchain.pem && -f nginx/ssl/privkey.pem ]]; then
  ok "SSL cert already present in nginx/ssl/"
else
  log "Generating self-signed SSL certificate (replace with Let's Encrypt for production)..."
  if ! command -v openssl >/dev/null 2>&1; then
    err "openssl required. Install: apt install openssl"
    exit 1
  fi
  CN=$(grep -E '^ALLOWED_HOSTS=' .env | head -n1 | cut -d= -f2 | tr ',' '\n' | tail -n1 | tr -d ' ')
  CN=${CN:-localhost}
  openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout nginx/ssl/privkey.pem \
    -out    nginx/ssl/fullchain.pem \
    -subj   "/C=BD/ST=Dhaka/L=Dhaka/O=ISP/CN=${CN}" 2>/dev/null
  chmod 600 nginx/ssl/privkey.pem
  ok "Self-signed cert created for ${CN}"
fi

# ── 4. Build and start ─────────────────────────────────────
log "Building containers (this can take 5-10 minutes the first time)..."
$COMPOSE build

log "Starting the stack in detached mode..."
$COMPOSE up -d

log "Waiting for the database to be ready..."
for i in {1..60}; do
  if $COMPOSE exec -T db pg_isready -U "$(grep '^DB_USER=' .env | cut -d= -f2)" >/dev/null 2>&1; then
    ok "Postgres is ready"
    break
  fi
  sleep 2
  [[ $i -eq 60 ]] && { err "Postgres did not become ready in 120s"; $COMPOSE logs db | tail -n 30; exit 1; }
done

log "Waiting for the backend container to start..."
for i in {1..60}; do
  if $COMPOSE exec -T backend python -c "print('up')" >/dev/null 2>&1; then
    ok "Backend container is responsive"
    break
  fi
  sleep 2
done

# First run: generate initial migrations for every app (no-ops on subsequent runs).
log "Generating initial migrations (first deploy only - idempotent)..."
$COMPOSE exec -T backend python manage.py makemigrations --noinput accounts customers billing payments packages network support inventory reseller reports hr notifications || true
$COMPOSE exec -T backend python manage.py makemigrations --noinput || true

log "Running database migrations..."
$COMPOSE exec -T backend python manage.py migrate --noinput

log "Collecting static files..."
$COMPOSE exec -T backend python manage.py collectstatic --noinput >/dev/null

# ── 4b. Optional: seed demo data ───────────────────────────
if [[ "$NON_INTERACTIVE" != "1" ]]; then
  read -r -p "Seed the database with 50 demo customers (invoices, payments, tickets)? [y/N]: " seed_choice
  if [[ "$seed_choice" =~ ^[Yy]$ ]]; then
    log "Seeding demo data..."
    $COMPOSE exec -T backend python manage.py seed_demo_data || \
      warn "Seed failed - you can re-run later: $COMPOSE exec backend python manage.py seed_demo_data"
  fi
fi

# ── 5. Superuser ───────────────────────────────────────────
if [[ "$NON_INTERACTIVE" == "1" ]]; then
  warn "Skipping superuser creation in non-interactive mode."
  warn "Run later: $COMPOSE exec backend python manage.py createsuperuser"
else
  if $COMPOSE exec -T backend python -c "
import django; django.setup()
from django.contrib.auth import get_user_model
exit(0 if get_user_model().objects.filter(is_superuser=True).exists() else 1)
" 2>/dev/null; then
    ok "A superuser already exists - skipping creation."
  else
    log "Creating Django superuser..."
    $COMPOSE exec backend python manage.py createsuperuser || \
      warn "Superuser creation skipped/failed. Re-run: $COMPOSE exec backend python manage.py createsuperuser"
  fi
fi

# ── 6. Done ────────────────────────────────────────────────
DOMAIN_FROM_ENV=$(grep -E '^ALLOWED_HOSTS=' .env | head -n1 | cut -d= -f2 | tr ',' '\n' | tail -n1 | tr -d ' ')
DOMAIN_FROM_ENV=${DOMAIN_FROM_ENV:-localhost}
HTTP_PORT=$(grep -E '^HTTP_PORT='  .env | cut -d= -f2 || echo 80)
HTTPS_PORT=$(grep -E '^HTTPS_PORT=' .env | cut -d= -f2 || echo 443)

cat <<EOF

${GRN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}
${GRN}  ISP Software is up.${NC}
${GRN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}

  Web app:        https://${DOMAIN_FROM_ENV}:${HTTPS_PORT}/
                  http://${DOMAIN_FROM_ENV}:${HTTP_PORT}/   (will redirect to https)
  Admin panel:    https://${DOMAIN_FROM_ENV}:${HTTPS_PORT}/admin/
  API docs:       https://${DOMAIN_FROM_ENV}:${HTTPS_PORT}/api/v1/docs/
  Flower (celery): http://${DOMAIN_FROM_ENV}:5555/
  RADIUS auth:    UDP ${DOMAIN_FROM_ENV}:1812
  RADIUS acct:    UDP ${DOMAIN_FROM_ENV}:1813

  Useful commands:
    ${COMPOSE} ps                       # container status
    ${COMPOSE} logs -f backend          # tail backend logs
    ${COMPOSE} exec backend bash        # shell into backend
    ${COMPOSE} --profile tools up -d pgadmin   # start pgAdmin (port 5050)
    ${COMPOSE} down                     # stop all
    ${COMPOSE} down -v                  # stop + delete data (DESTRUCTIVE)

  Replace the self-signed cert in nginx/ssl/ with a real Let's Encrypt
  certificate before going live. See nginx/ssl/README.md.

EOF
