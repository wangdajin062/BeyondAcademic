#!/usr/bin/env bash
set -euo pipefail

# BeyondAcademic Alibaba Cloud ECS deployment helper
# Usage:
#   DOMAIN=example.com SERVER_IP=1.2.3.4 EMAIL=ops@example.com ./scripts/deploy_aliyun_ecs.sh

REQUIRED_CMDS=(git curl openssl docker python3)
for cmd in "${REQUIRED_CMDS[@]}"; do
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "[ERROR] Missing required command: $cmd"
    exit 1
  fi
done

if ! docker compose version >/dev/null 2>&1; then
  echo "[ERROR] docker compose plugin is required"
  exit 1
fi

DOMAIN="${DOMAIN:-}"
SERVER_IP="${SERVER_IP:-}"
EMAIL="${EMAIL:-}"
APP_DIR="${APP_DIR:-/opt/BeyondAcademic}"
GIT_URL="${GIT_URL:-https://github.com/wangdajin062/BeyondAcademic.git}"
BRANCH="${BRANCH:-main}"
ENABLE_TEST_AUTH="${ENABLE_TEST_AUTH:-false}"
WWW_DOMAIN="${WWW_DOMAIN:-true}"

if [[ -z "$DOMAIN" ]]; then
  echo "[ERROR] DOMAIN is required"
  exit 1
fi

if [[ -z "$EMAIL" ]]; then
  echo "[ERROR] EMAIL is required"
  exit 1
fi

mkdir -p "$APP_DIR"
if [[ ! -d "$APP_DIR/.git" ]]; then
  git clone "$GIT_URL" "$APP_DIR"
fi

cd "$APP_DIR"
git fetch --all --prune
git checkout "$BRANCH"
git pull --ff-only

if [[ ! -f .env ]]; then
  cp config/.env.example .env
fi

DB_PASSWORD="${DB_PASSWORD:-$(openssl rand -hex 16)}"
SECRET_KEY="${SECRET_KEY:-$(openssl rand -hex 32)}"
OPENAI_API_KEY="${OPENAI_API_KEY:-}"
ALLOWED_ORIGINS_DEFAULT="https://$DOMAIN"
if [[ -n "$SERVER_IP" ]]; then
  ALLOWED_ORIGINS_DEFAULT="$ALLOWED_ORIGINS_DEFAULT,http://$SERVER_IP,https://$SERVER_IP"
fi
ALLOWED_ORIGINS="${ALLOWED_ORIGINS:-$ALLOWED_ORIGINS_DEFAULT}"
DEFAULT_TEST_LOGIN_ACCOUNTS='{"tester":"test123456","researcher":"Research@2026"}'
TEST_LOGIN_ACCOUNTS="${TEST_LOGIN_ACCOUNTS:-$DEFAULT_TEST_LOGIN_ACCOUNTS}"

export DOMAIN SERVER_IP DB_PASSWORD SECRET_KEY OPENAI_API_KEY ALLOWED_ORIGINS ENABLE_TEST_AUTH TEST_LOGIN_ACCOUNTS WWW_DOMAIN
python3 - <<'PY'
import os
import re
from pathlib import Path

# Update .env
env_file = Path('.env')
lines = env_file.read_text().splitlines()
updates = {
    'DB_PASSWORD': os.environ['DB_PASSWORD'],
    'SECRET_KEY': os.environ['SECRET_KEY'],
    'OPENAI_API_KEY': os.environ['OPENAI_API_KEY'],
    'ALLOWED_ORIGINS': os.environ['ALLOWED_ORIGINS'],
    'ENABLE_TEST_AUTH': os.environ['ENABLE_TEST_AUTH'],
    'TEST_LOGIN_ACCOUNTS': os.environ['TEST_LOGIN_ACCOUNTS'],
}
found = set()
out = []
for line in lines:
    if '=' in line and not line.strip().startswith('#'):
        key = line.split('=', 1)[0]
        if key in updates:
            out.append(f"{key}={updates[key]}")
            found.add(key)
            continue
    out.append(line)
for key, value in updates.items():
    if key not in found:
        out.append(f"{key}={value}")
env_file.write_text('\n'.join(out) + '\n')

# Update nginx server_name and cert path domain placeholder
conf_path = Path('nginx/conf.d/beyondacademic.conf')
content = conf_path.read_text()

domain = os.environ['DOMAIN']
server_ip = os.environ.get('SERVER_IP', '').strip()
www_domain = os.environ.get('WWW_DOMAIN', 'true').lower() == 'true'

names = [domain]
if www_domain:
    names.append(f"www.{domain}")
if server_ip:
    names.append(server_ip)
server_name = ' '.join(names)

content = re.sub(r"server_name\s+_;", f"server_name {server_name};", content, count=2)
content = content.replace('yourdomain.com', domain)

conf_path.write_text(content)
PY

mkdir -p certbot/conf certbot/www backend/logs frontend/build

docker compose -f docker-compose.prod.yml build backend
docker compose -f docker-compose.prod.yml up -d db redis backend nginx

CERTBOT_ARGS=(
  certonly --webroot
  --webroot-path=/var/www/certbot
  --email "$EMAIL"
  --agree-tos --no-eff-email
  -d "$DOMAIN"
)
if [[ "$WWW_DOMAIN" == "true" ]]; then
  CERTBOT_ARGS+=( -d "www.$DOMAIN" )
fi

docker compose -f docker-compose.prod.yml run --rm certbot "${CERTBOT_ARGS[@]}"

docker compose -f docker-compose.prod.yml restart nginx

echo "[OK] Deployment finished"
echo "- URL: https://$DOMAIN"
[[ -n "$SERVER_IP" ]] && echo "- IP access: http://$SERVER_IP"
echo "- Health: https://$DOMAIN/health"
echo "- API docs: https://$DOMAIN/docs"
