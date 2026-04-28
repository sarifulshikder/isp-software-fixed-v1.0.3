#!/bin/bash
# ═══════════════════════════════════════════════════════
# ISP Management Software - Control Script
# Usage: ./isp.sh [start|stop|restart|logs|status|backup|update|shell]
# ═══════════════════════════════════════════════════════

set -e
COMPOSE="docker compose"
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

banner() {
  echo -e "${BLUE}"
  echo "  ╔═══════════════════════════════════════╗"
  echo "  ║   📡 ISP Management Software v1.0    ║"
  echo "  ╚═══════════════════════════════════════╝"
  echo -e "${NC}"
}

check_env() {
  if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠  .env file not found. Copying from .env.example...${NC}"
    cp .env.example .env
    echo -e "${RED}⚠  Please edit .env with your settings before starting!${NC}"
    exit 1
  fi
}

cmd_start() {
  banner
  check_env
  echo -e "${GREEN}▶ Starting ISP Management Software...${NC}"
  $COMPOSE up -d --build
  echo ""
  echo -e "${GREEN}✅ All services started!${NC}"
  echo ""
  echo -e "  🌐 Web App:      ${BLUE}http://localhost${NC}"
  echo -e "  📚 API Docs:     ${BLUE}http://localhost/api/docs/${NC}"
  echo -e "  🔧 Admin:        ${BLUE}http://localhost/admin/${NC}"
  echo -e "  🌸 Flower:       ${BLUE}http://localhost:5555${NC}"
  echo ""
}

cmd_stop() {
  echo -e "${YELLOW}⏹ Stopping all services...${NC}"
  $COMPOSE down
  echo -e "${GREEN}✅ All services stopped.${NC}"
}

cmd_restart() {
  cmd_stop
  sleep 2
  cmd_start
}

cmd_logs() {
  SERVICE=${2:-""}
  $COMPOSE logs -f --tail=100 $SERVICE
}

cmd_status() {
  echo -e "${BLUE}📊 Service Status:${NC}"
  $COMPOSE ps
}

cmd_backup() {
  DATE=$(date +%Y%m%d_%H%M%S)
  BACKUP_DIR="backups/$DATE"
  mkdir -p $BACKUP_DIR
  echo -e "${GREEN}💾 Creating database backup...${NC}"
  $COMPOSE exec -T db pg_dump -U ispuser ispdb > $BACKUP_DIR/database.sql
  echo -e "${GREEN}✅ Backup saved to $BACKUP_DIR/database.sql${NC}"
}

cmd_restore() {
  BACKUP_FILE=$2
  if [ -z "$BACKUP_FILE" ]; then
    echo -e "${RED}❌ Usage: ./isp.sh restore <backup_file.sql>${NC}"
    exit 1
  fi
  echo -e "${YELLOW}⚠  Restoring database from $BACKUP_FILE...${NC}"
  $COMPOSE exec -T db psql -U ispuser ispdb < $BACKUP_FILE
  echo -e "${GREEN}✅ Database restored.${NC}"
}

cmd_shell() {
  SERVICE=${2:-"backend"}
  echo -e "${GREEN}🐚 Opening shell in $SERVICE container...${NC}"
  $COMPOSE exec $SERVICE sh
}

cmd_django() {
  $COMPOSE exec backend python manage.py ${@:2}
}

cmd_createsuperuser() {
  $COMPOSE exec backend python manage.py createsuperuser
}

cmd_update() {
  echo -e "${GREEN}🔄 Updating ISP Software...${NC}"
  git pull
  $COMPOSE build --no-cache
  $COMPOSE up -d
  $COMPOSE exec backend python manage.py migrate
  $COMPOSE exec backend python manage.py collectstatic --noinput
  echo -e "${GREEN}✅ Update complete!${NC}"
}

cmd_help() {
  banner
  echo "Usage: ./isp.sh <command>"
  echo ""
  echo "Commands:"
  echo "  start              Start all services"
  echo "  stop               Stop all services"
  echo "  restart            Restart all services"
  echo "  status             Show service status"
  echo "  logs [service]     View logs (optional: backend/nginx/db/redis/celery)"
  echo "  backup             Backup database"
  echo "  restore <file>     Restore database from backup"
  echo "  shell [service]    Open shell in container"
  echo "  django <cmd>       Run Django management command"
  echo "  createsuperuser    Create admin user"
  echo "  update             Pull latest and update"
  echo ""
}

# Main
case "$1" in
  start)            cmd_start ;;
  stop)             cmd_stop ;;
  restart)          cmd_restart ;;
  logs)             cmd_logs "$@" ;;
  status)           cmd_status ;;
  backup)           cmd_backup ;;
  restore)          cmd_restore "$@" ;;
  shell)            cmd_shell "$@" ;;
  django)           cmd_django "$@" ;;
  createsuperuser)  cmd_createsuperuser ;;
  update)           cmd_update ;;
  help|--help|-h)   cmd_help ;;
  *)                cmd_help ;;
esac
