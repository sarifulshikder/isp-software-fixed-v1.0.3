#!/usr/bin/env bash
# =============================================================================
# ISP Management Software - Management Script (Fixed v1.0.3)
# =============================================================================
set -euo pipefail

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'
BLUE='\033[0;34m'; BOLD='\033[1m'; NC='\033[0m'

ok()   { echo -e "${GREEN}✔${NC}  $*"; }
info() { echo -e "${BLUE}ℹ${NC}  $*"; }
warn() { echo -e "${YELLOW}⚠${NC}  $*"; }
err()  { echo -e "${RED}✘${NC}  $*"; exit 1; }

# ── Docker permission fix ─────────────────────────────────────────────────────
if ! docker info &>/dev/null 2>&1; then
    DC="sudo docker compose"
    DK="sudo docker"
else
    DC="docker compose"
    DK="docker"
fi

# ── Ensure we are in project directory ───────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# ── Banner ────────────────────────────────────────────────────────────────────
banner() {
    echo -e "${BOLD}${BLUE}"
    echo "  ╔══════════════════════════════════════╗"
    echo "  ║   ISP Management Software v1.0.3    ║"
    echo "  ╚══════════════════════════════════════╝"
    echo -e "${NC}"
}

# =============================================================================
CMD="${1:-help}"
shift || true

case "$CMD" in

# ── start ─────────────────────────────────────────────────────────────────────
start)
    banner
    info "Starting ISP Management Software..."
    $DC up -d
    ok "All services started"
    echo ""
    $DC ps
    ;;

# ── stop ──────────────────────────────────────────────────────────────────────
stop)
    info "Stopping all services..."
    $DC stop
    ok "All services stopped"
    ;;

# ── restart ───────────────────────────────────────────────────────────────────
restart)
    info "Restarting all services..."
    $DC restart
    ok "All services restarted"
    ;;

# ── status ────────────────────────────────────────────────────────────────────
status)
    banner
    echo -e "${BOLD}Service Status:${NC}"
    $DC ps
    ;;

# ── logs ──────────────────────────────────────────────────────────────────────
logs)
    SERVICE="${1:-}"
    if [[ -n "$SERVICE" ]]; then
        $DC logs -f "$SERVICE"
    else
        $DC logs -f --tail=100
    fi
    ;;

# ── backup ────────────────────────────────────────────────────────────────────
backup)
    BACKUP_FILE="backup_$(date +%Y%m%d_%H%M%S).sql"
    info "Creating database backup: $BACKUP_FILE"
    $DC exec -T db pg_dump -U ispuser ispdb > "$BACKUP_FILE"
    ok "Backup saved: $BACKUP_FILE"
    ;;

# ── restore ───────────────────────────────────────────────────────────────────
restore)
    FILE="${1:-}"
    [[ -z "$FILE" ]] && err "Usage: ./isp.sh restore <backup.sql>"
    [[ ! -f "$FILE" ]] && err "File not found: $FILE"
    warn "This will OVERWRITE the current database. Continue? (yes/no)"
    read -r CONFIRM
    [[ "$CONFIRM" != "yes" ]] && { info "Cancelled."; exit 0; }
    info "Restoring from $FILE..."
    $DC exec -T db psql -U ispuser -d ispdb < "$FILE"
    ok "Database restored"
    ;;

# ── shell ─────────────────────────────────────────────────────────────────────
shell)
    SERVICE="${1:-backend}"
    info "Opening shell in $SERVICE container..."
    $DC exec "$SERVICE" /bin/sh
    ;;

# ── django ────────────────────────────────────────────────────────────────────
django)
    $DC exec backend python manage.py "$@"
    ;;

# ── createsuperuser ───────────────────────────────────────────────────────────
createsuperuser)
    info "Creating superuser..."
    read -rp "Email [admin@isp.com]: " SU_EMAIL
    SU_EMAIL="${SU_EMAIL:-admin@isp.com}"
    read -rsp "Password: " SU_PASS
    echo ""

    $DC exec -T backend python manage.py shell << PYEOF
from django.contrib.auth import get_user_model
User = get_user_model()
email = "${SU_EMAIL}"
password = "${SU_PASS}"
username = email.split('@')[0]
if not User.objects.filter(email=email).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f"[OK] Superuser created: {email}")
else:
    u = User.objects.get(email=email)
    u.set_password(password)
    u.save()
    print(f"[OK] Password updated for: {email}")
PYEOF
    ok "Done"
    ;;

# ── update ────────────────────────────────────────────────────────────────────
update)
    info "Pulling latest changes..."
    git pull
    info "Rebuilding containers..."
    $DC build --parallel
    $DC up -d
    $DC exec -T backend python manage.py migrate --noinput
    $DC exec -T backend python manage.py collectstatic --noinput
    ok "Update complete"
    ;;

# ── help ──────────────────────────────────────────────────────────────────────
help|*)
    banner
    echo -e "${BOLD}Usage:${NC} ./isp.sh <command> [options]"
    echo ""
    echo -e "${BOLD}Commands:${NC}"
    echo "  start              Start all services"
    echo "  stop               Stop all services"
    echo "  restart            Restart all services"
    echo "  status             Show service status"
    echo "  logs [service]     View logs (all or specific service)"
    echo "  backup             Backup database"
    echo "  restore <file>     Restore database from backup"
    echo "  shell [service]    Open shell in container (default: backend)"
    echo "  django <cmd>       Run Django management command"
    echo "  createsuperuser    Create admin user interactively"
    echo "  update             Pull latest code and restart"
    echo ""
    echo -e "${BOLD}Examples:${NC}"
    echo "  ./isp.sh logs backend"
    echo "  ./isp.sh django migrate"
    echo "  ./isp.sh backup"
    ;;

esac