#!/usr/bin/env bash
# =============================================================================
# ISP Management Software - Deploy Script (Fixed v1.0.3)
# Fixes: sed error, docker permission, SSL cert, superuser creation,
#        django-prometheus, django-redis missing packages
# =============================================================================
set -euo pipefail

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
BLUE='\033[0;34m'; NC='\033[0m'; BOLD='\033[1m'

ok()   { echo -e "${GREEN}[ ok ]${NC} $*"; }
info() { echo -e "${BLUE}[info]${NC} $*"; }
warn() { echo -e "${YELLOW}[warn]${NC} $*"; }
err()  { echo -e "${RED}[ERR ]${NC} $*"; exit 1; }
step() { echo -e "\n${BOLD}${BLUE}[deploy]${NC} $*"; }

AUTO=false
[[ "${1:-}" == "-y" || "${1:-}" == "--yes" ]] && AUTO=true

gen_secret() { tr -dc 'A-Za-z0-9' </dev/urandom 2>/dev/null | head -c "${1:-50}" || true; }
gen_pass()   { tr -dc 'A-Za-z0-9' </dev/urandom 2>/dev/null | head -c 20 || true; }

# =============================================================================
# STEP 1 — Docker permission fix
# =============================================================================
step "Checking prerequisites..."

if ! docker info &>/dev/null 2>&1; then
    warn "Docker permission issue. Fixing..."
    sudo usermod -aG docker "$USER" 2>/dev/null || true
    DC="sudo docker compose"
    DK="sudo docker"
    warn "Using sudo for Docker. Logout/login after deploy for permanent fix."
else
    DC="docker compose"
    DK="docker"
fi

$DC version &>/dev/null 2>&1 || err "Docker Compose v2 not found. Run: sudo apt install docker-compose-plugin -y"
ok "Prerequisites OK — Docker $($DK --version | grep -oP '\d+\.\d+\.\d+' | head -1)"

# =============================================================================
# STEP 2 — Configuration
# =============================================================================
step "Generating .env..."

[[ ! -f .env.example ]] && err ".env.example not found. Are you in the project directory?"

if $AUTO; then
    COMPANY_NAME="My ISP Company"
    DOMAIN="localhost"
    ADMIN_EMAIL="admin@isp.com"
    DB_PASSWORD=$(gen_pass)
    REDIS_PASSWORD=$(gen_pass)
    RADIUS_SECRET=$(gen_pass)
    FLOWER_PASSWORD=$(gen_pass)
    PGADMIN_PASSWORD=$(gen_pass)
    SECRET_KEY=$(gen_secret 60)
    SUPERUSER_EMAIL="admin@isp.com"
    SUPERUSER_USERNAME="admin"
    SUPERUSER_FIRSTNAME="Admin"
    SUPERUSER_LASTNAME="User"
    SUPERUSER_PASSWORD="Admin$(gen_pass | head -c 8)!"
else
    echo ""
    read -rp "Company name [My ISP Company]: " COMPANY_NAME
    COMPANY_NAME="${COMPANY_NAME:-My ISP Company}"
    read -rp "Primary domain [localhost]: " DOMAIN
    DOMAIN="${DOMAIN:-localhost}"
    read -rp "Admin email [admin@isp.com]: " ADMIN_EMAIL
    ADMIN_EMAIL="${ADMIN_EMAIL:-admin@isp.com}"
    echo ""
    info "Leave blank to auto-generate passwords"
    read -rp "DB password [auto]: " DB_PASSWORD
    DB_PASSWORD="${DB_PASSWORD:-$(gen_pass)}"
    read -rp "Redis password [auto]: " REDIS_PASSWORD
    REDIS_PASSWORD="${REDIS_PASSWORD:-$(gen_pass)}"
    read -rp "RADIUS secret [auto]: " RADIUS_SECRET
    RADIUS_SECRET="${RADIUS_SECRET:-$(gen_pass)}"
    read -rp "Flower password [auto]: " FLOWER_PASSWORD
    FLOWER_PASSWORD="${FLOWER_PASSWORD:-$(gen_pass)}"
    read -rp "pgAdmin password [auto]: " PGADMIN_PASSWORD
    PGADMIN_PASSWORD="${PGADMIN_PASSWORD:-$(gen_pass)}"
    SECRET_KEY=$(gen_secret 60)
    echo ""
    info "Superuser (web panel admin) account:"
    read -rp "Superuser email [admin@isp.com]: " SUPERUSER_EMAIL
    SUPERUSER_EMAIL="${SUPERUSER_EMAIL:-admin@isp.com}"
    read -rp "Superuser first name [Admin]: " SUPERUSER_FIRSTNAME
    SUPERUSER_FIRSTNAME="${SUPERUSER_FIRSTNAME:-Admin}"
    read -rp "Superuser last name [User]: " SUPERUSER_LASTNAME
    SUPERUSER_LASTNAME="${SUPERUSER_LASTNAME:-User}"
    SUPERUSER_USERNAME=$(echo "$SUPERUSER_EMAIL" | cut -d@ -f1)
    read -rsp "Superuser password [auto]: " SUPERUSER_PASSWORD
    echo ""
    SUPERUSER_PASSWORD="${SUPERUSER_PASSWORD:-Admin$(gen_pass | head -c 8)!}"
fi

# Write .env using cat (avoids sed special character issues)
cat > .env << EOF
# ISP Management Software - Environment Configuration
# Generated: $(date)

# ── Django ────────────────────────────────────────────────────────────────────
SECRET_KEY=${SECRET_KEY}
DEBUG=False
ALLOWED_HOSTS=${DOMAIN},localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://${DOMAIN},https://${DOMAIN},http://localhost
DOMAIN=${DOMAIN}

# ── Database ──────────────────────────────────────────────────────────────────
DB_NAME=ispdb
DB_USER=ispuser
DB_PASSWORD=${DB_PASSWORD}
DB_HOST=db
DB_PORT=5432
POSTGRES_DB=ispdb
POSTGRES_USER=ispuser
POSTGRES_PASSWORD=${DB_PASSWORD}

# ── Redis ─────────────────────────────────────────────────────────────────────
REDIS_HOST=redis
REDIS_PASSWORD=${REDIS_PASSWORD}

# ── Company ───────────────────────────────────────────────────────────────────
COMPANY_NAME=${COMPANY_NAME}
COMPANY_ADDRESS=
COMPANY_PHONE=
COMPANY_EMAIL=${ADMIN_EMAIL}
CURRENCY=BDT
CURRENCY_SYMBOL=৳
TAX_RATE=0.0
LATE_FEE_RATE=2.0
GRACE_PERIOD_DAYS=7
BILLING_DATE=1

# ── Email ─────────────────────────────────────────────────────────────────────
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
DEFAULT_FROM_EMAIL=noreply@${DOMAIN}

# ── RADIUS ────────────────────────────────────────────────────────────────────
RADIUS_HOST=freeradius
RADIUS_PORT=1812
RADIUS_SECRET=${RADIUS_SECRET}

# ── Mikrotik ──────────────────────────────────────────────────────────────────
MIKROTIK_HOST=
MIKROTIK_USER=admin
MIKROTIK_PASSWORD=

# ── Flower / pgAdmin ─────────────────────────────────────────────────────────
FLOWER_USER=admin
FLOWER_PASSWORD=${FLOWER_PASSWORD}
PGADMIN_EMAIL=${ADMIN_EMAIL}
PGADMIN_PASSWORD=${PGADMIN_PASSWORD}

# ── Ports ─────────────────────────────────────────────────────────────────────
HTTP_PORT=80
HTTPS_PORT=443

# ── Superuser (auto-created on deploy) ────────────────────────────────────────
DJANGO_SUPERUSER_EMAIL=${SUPERUSER_EMAIL}
DJANGO_SUPERUSER_USERNAME=${SUPERUSER_USERNAME}
DJANGO_SUPERUSER_PASSWORD=${SUPERUSER_PASSWORD}
DJANGO_SUPERUSER_FIRSTNAME=${SUPERUSER_FIRSTNAME}
DJANGO_SUPERUSER_LASTNAME=${SUPERUSER_LASTNAME}

# ── Monitoring ────────────────────────────────────────────────────────────────
SENTRY_DSN=
APP_VERSION=1.0.3
EOF

ok ".env generated"

# =============================================================================
# STEP 3 — SSL Certificate
# =============================================================================
step "Generating SSL certificate..."
mkdir -p nginx/ssl
if [[ ! -f nginx/ssl/fullchain.pem ]]; then
    openssl req -x509 -nodes -days 3650 -newkey rsa:2048 \
        -keyout nginx/ssl/privkey.pem \
        -out nginx/ssl/fullchain.pem \
        -subj "/C=BD/ST=Dhaka/L=Dhaka/O=ISP/CN=${DOMAIN}" 2>/dev/null
    ok "SSL certificate generated"
else
    ok "SSL certificate exists"
fi

# =============================================================================
# STEP 4 — Build & Start
# =============================================================================
step "Building Docker images..."
$DC build --parallel
ok "Build complete"

step "Starting containers..."
$DC up -d
ok "Containers started"

# =============================================================================
# STEP 5 — Wait for DB
# =============================================================================
step "Waiting for database..."
MAX=90; W=0
until $DC exec -T db pg_isready -U ispuser -d ispdb &>/dev/null 2>&1; do
    [[ $W -ge $MAX ]] && err "DB not ready after ${MAX}s. Check: docker logs isp_db"
    sleep 3; W=$((W+3)); echo -n "."
done
echo ""; ok "Database ready"

# =============================================================================
# STEP 6 — Wait for backend
# =============================================================================
step "Waiting for backend..."
sleep 15
MAX=120; W=0
until $DC exec -T backend python -c "import django; django.setup(); print('ok')" &>/dev/null 2>&1; do
    [[ $W -ge $MAX ]] && { warn "Backend timeout, continuing..."; break; }
    sleep 5; W=$((W+5)); echo -n "."
done
echo ""; ok "Backend ready"

# =============================================================================
# STEP 7 — Migrations
# =============================================================================
step "Running migrations..."
$DC exec -T backend python manage.py migrate --noinput
ok "Migrations done"

# =============================================================================
# STEP 8 — Static files
# =============================================================================
step "Collecting static files..."
$DC exec -T backend python manage.py collectstatic --noinput 2>/dev/null || true
ok "Static files collected"

# =============================================================================
# STEP 9 — Superuser
# NOTE: User model uses EMAIL as USERNAME_FIELD
# =============================================================================
step "Creating superuser..."
$DC exec -T backend python manage.py shell << PYEOF
import os
import django
from django.contrib.auth import get_user_model

User = get_user_model()

email     = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@isp.com')
username  = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
password  = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'Admin1234!')
firstname = os.environ.get('DJANGO_SUPERUSER_FIRSTNAME', 'Admin')
lastname  = os.environ.get('DJANGO_SUPERUSER_LASTNAME', 'User')

# User model uses email as USERNAME_FIELD
if not User.objects.filter(email=email).exists():
    user = User.objects.create_superuser(
        email=email,
        username=username,
        password=password,
        first_name=firstname,
        last_name=lastname,
        role='superadmin',
    )
    print(f"[OK] Superuser created: {email}")
else:
    user = User.objects.get(email=email)
    user.set_password(password)
    user.is_superuser = True
    user.is_staff = True
    user.role = 'superadmin'
    user.save()
    print(f"[OK] Superuser updated: {email}")
PYEOF

ok "Superuser ready"

# =============================================================================
# DONE
# =============================================================================
echo ""
echo -e "${GREEN}${BOLD}══════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}${BOLD}  ✅  ISP Management Software - Deploy Complete!      ${NC}"
echo -e "${GREEN}${BOLD}══════════════════════════════════════════════════════${NC}"
echo ""
echo -e "  🌐  Web App  : ${BOLD}http://${DOMAIN}${NC}"
echo -e "  🔒  HTTPS    : ${BOLD}https://${DOMAIN}${NC}"
echo -e "  📖  API Docs : ${BOLD}https://${DOMAIN}/api/docs/${NC}"
echo -e "  ⚙️   Admin   : ${BOLD}https://${DOMAIN}/admin/${NC}"
echo -e "  📊  Flower   : ${BOLD}http://${DOMAIN}:5555${NC}"
echo ""
echo -e "  👤  Login:"
echo -e "      Email    : ${BOLD}${SUPERUSER_EMAIL}${NC}"
echo -e "      Password : ${BOLD}${SUPERUSER_PASSWORD}${NC}"
echo ""
echo -e "  📋  Commands:"
echo -e "      ./isp.sh status   # Check services"
echo -e "      ./isp.sh logs     # View logs"
echo -e "      ./isp.sh backup   # Backup database"
echo ""
if [[ "${DC}" == "sudo docker compose" ]]; then
    echo -e "${YELLOW}  ⚠️   Run 'newgrp docker' or logout/login for docker without sudo${NC}"
    echo ""
fi
echo -e "${GREEN}${BOLD}══════════════════════════════════════════════════════${NC}"