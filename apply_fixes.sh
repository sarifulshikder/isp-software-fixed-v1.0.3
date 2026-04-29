#!/usr/bin/env bash
# =============================================================================
# ISP Software - Apply All Fixes
# Run inside the project directory
# =============================================================================
set -e

GREEN='\033[0;32m'; BLUE='\033[0;34m'; YELLOW='\033[1;33m'; NC='\033[0m'; BOLD='\033[1m'
ok()   { echo -e "${GREEN}✔${NC} $*"; }
info() { echo -e "${BLUE}ℹ${NC} $*"; }
warn() { echo -e "${YELLOW}⚠${NC} $*"; }

echo -e "${BOLD}Applying all fixes to ISP Software v1.0.3...${NC}"
echo ""

# 1. Fix kombu version
info "Fixing celery/kombu conflict..."
sed -i 's/kombu==5\.3\.3/kombu==5.3.4/g' backend/requirements.txt 2>/dev/null || true
ok "kombu version fixed"

# 2. Add missing packages if not present
info "Adding missing packages..."
grep -q "django-redis" backend/requirements.txt || echo "django-redis==5.4.0" >> backend/requirements.txt
grep -q "django-prometheus" backend/requirements.txt || echo "django-prometheus==2.3.1" >> backend/requirements.txt
grep -q "django-environ" backend/requirements.txt || echo "django-environ==0.11.2" >> backend/requirements.txt
grep -q "django-import-export" backend/requirements.txt || echo "django-import-export==4.1.1" >> backend/requirements.txt
ok "Missing packages added"

# 3. Fix init_db.sql
info "Fixing database init script..."
cat > docker/scripts/init_db.sql << 'SQLEOF'
-- ISP Software - Database Init (Fixed v1.0.3)
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'ispuser') THEN
        CREATE USER ispuser WITH PASSWORD 'isppassword';
    END IF;
END
$$;

GRANT ALL PRIVILEGES ON DATABASE ispdb TO ispuser;

\c ispdb

GRANT ALL ON SCHEMA public TO ispuser;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO ispuser;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO ispuser;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO ispuser;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO ispuser;

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "unaccent";
SQLEOF
ok "init_db.sql fixed"

# 4. Docker permission
info "Fixing Docker permission..."
sudo usermod -aG docker "$USER" 2>/dev/null || true
ok "Docker group updated"

# 5. SSL certificate
info "Generating SSL certificate..."
mkdir -p nginx/ssl
if [[ ! -f nginx/ssl/fullchain.pem ]]; then
    openssl req -x509 -nodes -days 3650 -newkey rsa:2048 \
        -keyout nginx/ssl/privkey.pem \
        -out nginx/ssl/fullchain.pem \
        -subj "/C=BD/ST=Dhaka/L=Dhaka/O=ISP/CN=localhost" 2>/dev/null
    ok "SSL certificate generated"
else
    ok "SSL certificate already exists"
fi

# 6. Make scripts executable
chmod +x deploy.sh isp.sh 2>/dev/null || true
ok "Scripts are executable"

echo ""
echo -e "${GREEN}${BOLD}All fixes applied successfully!${NC}"
echo ""
echo "Now run:"
echo "  docker compose down -v"
echo "  ./deploy.sh -y"