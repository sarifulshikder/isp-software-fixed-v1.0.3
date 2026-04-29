#!/usr/bin/env bash
# =============================================================================
# ISP Software - Apply All Fixes Script
# Run this on your server inside the project directory
# =============================================================================
set -e

GREEN='\033[0;32m'; BLUE='\033[0;34m'; NC='\033[0m'; BOLD='\033[1m'
ok()   { echo -e "${GREEN}✔${NC} $*"; }
info() { echo -e "${BLUE}ℹ${NC} $*"; }

echo -e "${BOLD}Applying all fixes to ISP Software...${NC}"
echo ""

# 1. Fix kombu version in requirements.txt
info "Fixing celery/kombu version conflict..."
sed -i 's/kombu==5\.3\.3/kombu==5.3.4/g' backend/requirements.txt
# Also handle if kombu is not pinned or different version
grep -q "kombu" backend/requirements.txt || echo "kombu==5.3.4" >> backend/requirements.txt
ok "requirements.txt fixed"

# 2. Fix init_db.sql - create user before grant
info "Fixing database init script..."
cat > docker/scripts/init_db.sql << 'SQLEOF'
-- Create user if not exists (prevents error on re-deploy)
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'ispuser') THEN
        CREATE USER ispuser WITH PASSWORD 'isppassword';
    END IF;
END
$$;

-- Grant privileges
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

# 3. Fix Docker permission
info "Fixing Docker permission..."
sudo usermod -aG docker "$USER" 2>/dev/null || true
ok "Docker group added (takes effect after logout/login)"

# 4. Generate SSL certificate
info "Generating SSL certificate..."
mkdir -p nginx/ssl
if [[ ! -f nginx/ssl/fullchain.pem ]]; then
    openssl req -x509 -nodes -days 3650 -newkey rsa:2048 \
        -keyout nginx/ssl/privkey.pem \
        -out nginx/ssl/fullchain.pem \
        -subj "/C=BD/ST=Dhaka/L=Dhaka/O=ISP/CN=localhost" \
        2>/dev/null
    ok "SSL certificate generated"
else
    ok "SSL certificate already exists"
fi

# 5. Make scripts executable
chmod +x deploy.sh isp.sh 2>/dev/null || true
ok "Scripts made executable"

echo ""
echo -e "${GREEN}${BOLD}All fixes applied!${NC}"
echo ""
echo "Now run:"
echo "  docker compose down -v"
echo "  ./deploy.sh -y"