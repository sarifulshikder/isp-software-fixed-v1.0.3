#!/usr/bin/env bash
# =============================================================================
# ISP Management Software - Deploy Script (Fixed v1.0.3)
# Fixes: sed error, docker permission, SSL cert, superuser creation
# =============================================================================
set -euo pipefail

# ── Colors ────────────────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
BLUE='\033[0;34m'; NC='\033[0m'; BOLD='\033[1m'

ok()   { echo -e "${GREEN}[ ok ]${NC} $*"; }
info() { echo -e "${BLUE}[info]${NC} $*"; }
warn() { echo -e "${YELLOW}[warn]${NC} $*"; }
err()  { echo -e "${RED}[ERR ]${NC} $*"; exit 1; }
step() { echo -e "\n${BOLD}${BLUE}[deploy]${NC} $*"; }

# ── Non-interactive flag ──────────────────────────────────────────────────────
AUTO=false
[[ "${1:-}" == "-y" || "${1:-}" == "--yes" ]] && AUTO=true

# ── Helper: generate random secret ───────────────────────────────────────────
gen_secret() { tr -dc 'A-Za-z0-9!@#%^&*()_+=' </dev/urandom 2>/dev/null | head -c "${1:-50}" || true; }
gen_pass()   { tr -dc 'A-Za-z0-9' </dev/urandom 2>/dev/null | head -c 20 || true; }

# =============================================================================
# STEP 1 — Check prerequisites
# =============================================================================
step "Checking prerequisites..."

# Fix Docker permission automatically
if ! docker info &>/dev/null 2>&1; then
    warn "Docker permission issue detected. Fixing..."
    sudo usermod -aG docker "$USER" 2>/dev/null || true
    # Use sudo for this session
    DOCKER_CMD="sudo docker"
    COMPOSE_CMD="sudo docker compose"
    warn "Using sudo for Docker this session. Please logout/login after deploy for permanent fix."
else
    DOCKER_CMD="docker"
    COMPOSE_CMD="docker compose"
fi

# Check Docker version
DOCKER_VER=$($DOCKER_CMD --version 2>/dev/null | grep -oP '\d+\.\d+' | head -1 || echo "0")
ok "Docker: $($DOCKER_CMD --version)"

# Check Docker Compose
if $COMPOSE_CMD version &>/dev/null 2>&1; then
    ok "Compose: $($COMPOSE_CMD version)"
else
    err "Docker Compose v2 not found. Run: sudo apt install docker-compose-plugin -y"
fi

ok "Prerequisites check passed"

# =============================================================================
# STEP 2 — Gather configuration
# =============================================================================
step "Generating .env from .env.example..."

if [[ ! -f .env.example ]]; then
    err ".env.example not found. Are you in the project directory?"
fi

if $AUTO; then
    info "Auto mode: generating all secrets automatically"
    COMPANY_NAME="My ISP Company"
    DOMAIN="localhost"
    ADMIN_EMAIL="admin@isp.local"
    DB_PASSWORD=$(gen_pass)
    REDIS_PASSWORD=$(gen_pass)
    RADIUS_SECRET=$(gen_pass)
    FLOWER_PASSWORD=$(gen_pass)
    PGADMIN_PASSWORD=$(gen_pass)
    SECRET_KEY=$(gen_secret 60)
    SUPERUSER_EMAIL="admin@isp.com"
    SUPERUSER_PASSWORD="Admin$(gen_pass | head -c 8)!"
else
    echo ""
    read -rp "Company name [My Internet Service Provider]: " COMPANY_NAME
    COMPANY_NAME="${COMPANY_NAME:-My Internet Service Provider}"

    read -rp "Primary domain (no http://) [localhost]: " DOMAIN
    DOMAIN="${DOMAIN:-localhost}"

    read -rp "Admin email [admin@isp.com]: " ADMIN_EMAIL
    ADMIN_EMAIL="${ADMIN_EMAIL:-admin@isp.com}"

    echo ""
    info "Leave passwords blank to auto-generate strong passwords"
    read -rp "DB password [auto]: " DB_PASSWORD
    DB_PASSWORD="${DB_PASSWORD:-$(gen_pass)}"

    read -rp "Redis password [auto]: " REDIS_PASSWORD
    REDIS_PASSWORD="${REDIS_PASSWORD:-$(gen_pass)}"

    read -rp "RADIUS shared secret [auto]: " RADIUS_SECRET
    RADIUS_SECRET="${RADIUS_SECRET:-$(gen_pass)}"

    read -rp "Flower password [auto]: " FLOWER_PASSWORD
    FLOWER_PASSWORD="${FLOWER_PASSWORD:-$(gen_pass)}"

    read -rp "pgAdmin password [auto]: " PGADMIN_PASSWORD
    PGADMIN_PASSWORD="${PGADMIN_PASSWORD:-$(gen_pass)}"

    SECRET_KEY=$(gen_secret 60)

    echo ""
    info "Superuser (admin) account for the web panel:"
    read -rp "Superuser email [admin@isp.com]: " SUPERUSER_EMAIL
    SUPERUSER_EMAIL="${SUPERUSER_EMAIL:-admin@isp.com}"

    read -rsp "Superuser password [auto-generate]: " SUPERUSER_PASSWORD
    echo ""
    SUPERUSER_PASSWORD="${SUPERUSER_PASSWORD:-Admin$(gen_pass | head -c 8)!}"
fi

# Write .env file using cat (avoids sed special character issues)
cat > .env << EOF
# =============================================================================
# ISP Management Software - Environment Configuration
# Generated: $(date)
# =============================================================================

# ── Django ────────────────────────────────────────────────────────────────────
SECRET_KEY=${SECRET_KEY}
DEBUG=False
ALLOWED_HOSTS=${DOMAIN},localhost,127.0.0.1
DOMAIN=${DOMAIN}

# ── Database (PostgreSQL) ─────────────────────────────────────────────────────
DB_NAME=ispdb
DB_USER=ispuser
DB_PASSWORD=${DB_PASSWORD}
DB_HOST=db
DB_PORT=5432
POSTGRES_DB=ispdb
POSTGRES_USER=ispuser
POSTGRES_PASSWORD=${DB_PASSWORD}

# ── Redis ─────────────────────────────────────────────────────────────────────
REDIS_PASSWORD=${REDIS_PASSWORD}
REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/0
CELERY_BROKER_URL=redis://:${REDIS_PASSWORD}@redis:6379/0
CELERY_RESULT_BACKEND=redis://:${REDIS_PASSWORD}@redis:6379/0

# ── Email ─────────────────────────────────────────────────────────────────────
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
DEFAULT_FROM_EMAIL=noreply@${DOMAIN}

# ── Company ───────────────────────────────────────────────────────────────────
COMPANY_NAME=${COMPANY_NAME}
ADMIN_EMAIL=${ADMIN_EMAIL}

# ── RADIUS ────────────────────────────────────────────────────────────────────
RADIUS_SECRET=${RADIUS_SECRET}

# ── Flower ────────────────────────────────────────────────────────────────────
FLOWER_USER=admin
FLOWER_PASSWORD=${FLOWER_PASSWORD}

# ── pgAdmin ───────────────────────────────────────────────────────────────────
PGADMIN_EMAIL=${ADMIN_EMAIL}
PGADMIN_PASSWORD=${PGADMIN_PASSWORD}

# ── Superuser (auto-created on first deploy) ──────────────────────────────────
DJANGO_SUPERUSER_EMAIL=${SUPERUSER_EMAIL}
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_PASSWORD=${SUPERUSER_PASSWORD}

# ── SSL / Nginx ───────────────────────────────────────────────────────────────
HTTP_PORT=80
HTTPS_PORT=443
EOF

ok ".env generated"

# =============================================================================
# STEP 3 — Generate self-signed SSL certificate
# =============================================================================
step "Generating self-signed SSL certificate..."

mkdir -p nginx/ssl

if [[ ! -f nginx/ssl/fullchain.pem ]]; then
    openssl req -x509 -nodes -days 3650 -newkey rsa:2048 \
        -keyout nginx/ssl/privkey.pem \
        -out nginx/ssl/fullchain.pem \
        -subj "/C=BD/ST=Dhaka/L=Dhaka/O=ISP/CN=${DOMAIN}" \
        2>/dev/null
    ok "SSL certificate generated (valid 10 years)"
else
    ok "SSL certificate already exists, skipping"
fi

# =============================================================================
# STEP 4 — Build and start containers
# =============================================================================
step "Building and starting Docker containers..."
$COMPOSE_CMD build --parallel
$COMPOSE_CMD up -d

ok "Containers started"

# =============================================================================
# STEP 5 — Wait for services to be healthy
# =============================================================================
step "Waiting for database to be ready..."
MAX_WAIT=60
WAITED=0
until $COMPOSE_CMD exec -T db pg_isready -U ispuser -d ispdb &>/dev/null 2>&1; do
    if [[ $WAITED -ge $MAX_WAIT ]]; then
        err "Database did not become ready in ${MAX_WAIT}s. Check: docker logs isp_db"
    fi
    sleep 2
    WAITED=$((WAITED + 2))
    echo -n "."
done
echo ""
ok "Database is ready"

# =============================================================================
# STEP 6 — Wait for backend
# =============================================================================
step "Waiting for backend container to start..."
sleep 10

MAX_WAIT=90
WAITED=0
until $COMPOSE_CMD exec -T backend python manage.py check --deploy &>/dev/null 2>&1; do
    if [[ $WAITED -ge $MAX_WAIT ]]; then
        warn "Backend health check timed out, continuing anyway..."
        break
    fi
    sleep 3
    WAITED=$((WAITED + 3))
    echo -n "."
done
echo ""
ok "Backend is responsive"

# =============================================================================
# STEP 7 — Run migrations
# =============================================================================
step "Running database migrations..."
$COMPOSE_CMD exec -T backend python manage.py migrate --noinput
ok "Migrations complete"

# =============================================================================
# STEP 8 — Collect static files
# =============================================================================
step "Collecting static files..."
$COMPOSE_CMD exec -T backend python manage.py collectstatic --noinput --clear 2>/dev/null || \
$COMPOSE_CMD exec -T backend python manage.py collectstatic --noinput
ok "Static files collected"

# =============================================================================
# STEP 9 — Create superuser
# =============================================================================
step "Creating superuser..."
$COMPOSE_CMD exec -T backend python manage.py shell << 'PYEOF'
import os
import django
from django.contrib.auth import get_user_model

User = get_user_model()

email    = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@isp.com')
username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'Admin1234!')

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(
        username=username,
        email=email,
        password=password
    )
    print(f"[OK] Superuser created: {username} / {email}")
else:
    # Update password in case it changed
    u = User.objects.get(username=username)
    u.set_password(password)
    u.is_superuser = True
    u.is_staff = True
    u.save()
    print(f"[OK] Superuser already exists, password updated: {username}")
PYEOF

ok "Superuser ready"

# =============================================================================
# DONE — Show summary
# =============================================================================
echo ""
echo -e "${GREEN}${BOLD}════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}${BOLD}  ✅  ISP Management Software - Deploy Complete!    ${NC}"
echo -e "${GREEN}${BOLD}════════════════════════════════════════════════════${NC}"
echo ""
echo -e "  🌐  Web App  : ${BOLD}http://${DOMAIN}${NC}  (or  https://${DOMAIN})"
echo -e "  📖  API Docs : ${BOLD}http://${DOMAIN}/api/docs/${NC}"
echo -e "  ⚙️   Admin   : ${BOLD}http://${DOMAIN}/admin/${NC}"
echo -e "  📊  Flower   : ${BOLD}http://${DOMAIN}:5555${NC}"
echo ""
echo -e "  👤  Login credentials:"
echo -e "      Email    : ${BOLD}${SUPERUSER_EMAIL}${NC}"
echo -e "      Password : ${BOLD}${SUPERUSER_PASSWORD}${NC}"
echo ""
if ! docker info &>/dev/null 2>&1; then
    echo -e "${YELLOW}  ⚠️  Docker permission: Run 'newgrp docker' or logout/login${NC}"
    echo ""
fi
echo -e "  📋  Useful commands:"
echo -e "      ./isp.sh status    # Check services"
echo -e "      ./isp.sh logs      # View logs"
echo -e "      ./isp.sh restart   # Restart all"
echo -e "      ./isp.sh backup    # Backup database"
echo ""
echo -e "${GREEN}${BOLD}════════════════════════════════════════════════════${NC}"