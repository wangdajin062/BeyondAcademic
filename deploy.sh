#!/bin/bash
# BeyondAcademic生产环境快速部署脚本 / Quick Production Deployment Script

set -euo pipefail

echo "=================================="
echo "BeyondAcademic生产部署 / Production Deployment"
echo "=================================="

# 颜色定义 / Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查是否为root用户 / Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}此脚本需要root权限运行 / This script must be run as root${NC}"
   echo "请使用: sudo bash deploy.sh"
   exit 1
fi

# 支持非交互变量 / Support non-interactive env inputs
DOMAIN="${DOMAIN:-}"
SERVER_IP="${SERVER_IP:-}"
EMAIL="${EMAIL:-}"
CONFIGURE_SSL="${CONFIGURE_SSL:-}"
BRANCH="${BRANCH:-main}"
WWW_DOMAIN="${WWW_DOMAIN:-true}"

if [[ -z "$DOMAIN" ]]; then
  read -r -p "请输入您的域名 (例如: example.com) / Enter your domain (e.g., example.com): " DOMAIN
fi

if [[ -z "$DOMAIN" ]]; then
    echo -e "${RED}域名不能为空 / Domain cannot be empty${NC}"
    exit 1
fi

if [[ -z "$SERVER_IP" ]]; then
  read -r -p "请输入服务器公网IP(可选) / Enter server public IP (optional): " SERVER_IP || true
fi

echo -e "${GREEN}使用域名 / Using domain: $DOMAIN${NC}"
[[ -n "$SERVER_IP" ]] && echo -e "${GREEN}实例IP / Server IP: $SERVER_IP${NC}"

# 1. 更新系统 / Update system
echo -e "\n${YELLOW}[1/10] 更新系统... / Updating system...${NC}"
apt update && apt upgrade -y

# 2. 安装Docker / Install Docker
echo -e "\n${YELLOW}[2/10] 安装Docker... / Installing Docker...${NC}"
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
else
    echo "Docker已安装 / Docker already installed"
fi

# 3. 安装Docker Compose / Install Docker Compose
echo -e "\n${YELLOW}[3/10] 安装Docker Compose... / Installing Docker Compose...${NC}"
if ! docker compose version &> /dev/null; then
    apt install -y docker-compose-plugin
else
    echo "Docker Compose已安装 / Docker Compose already installed"
fi

# 4. 克隆仓库 / Clone repository
echo -e "\n${YELLOW}[4/10] 克隆仓库... / Cloning repository...${NC}"
if [ ! -d "/var/www/beyondacademic" ]; then
    mkdir -p /var/www/beyondacademic
    cd /var/www/beyondacademic
    git clone https://github.com/wangdajin062/BeyondAcademic.git .
else
    cd /var/www/beyondacademic
fi
git fetch --all --prune
git checkout "$BRANCH"
git pull --ff-only

# 5. 配置环境变量 / Configure environment
echo -e "\n${YELLOW}[5/10] 配置环境变量... / Configuring environment...${NC}"
if [ ! -f ".env" ]; then
    cp .env.production .env
fi

SECRET_KEY="${SECRET_KEY:-$(openssl rand -hex 32)}"
DB_PASSWORD="${DB_PASSWORD:-$(openssl rand -hex 16)}"
ALLOWED_ORIGINS_DEFAULT="https://$DOMAIN"
if [[ -n "$SERVER_IP" ]]; then
  ALLOWED_ORIGINS_DEFAULT="$ALLOWED_ORIGINS_DEFAULT,http://$SERVER_IP,https://$SERVER_IP"
fi
ALLOWED_ORIGINS="${ALLOWED_ORIGINS:-$ALLOWED_ORIGINS_DEFAULT}"

export DOMAIN SERVER_IP DB_PASSWORD SECRET_KEY ALLOWED_ORIGINS
python3 - <<'PY'
import os
from pathlib import Path

env_file = Path('.env')
lines = env_file.read_text().splitlines()
updates = {
    'DB_PASSWORD': os.environ['DB_PASSWORD'],
    'SECRET_KEY': os.environ['SECRET_KEY'],
    'ALLOWED_ORIGINS': os.environ['ALLOWED_ORIGINS'],
}
out = []
seen = set()
for line in lines:
    if '=' in line and not line.strip().startswith('#'):
        key = line.split('=', 1)[0]
        if key in updates:
            out.append(f"{key}={updates[key]}")
            seen.add(key)
            continue
    out.append(line)
for key, value in updates.items():
    if key not in seen:
        out.append(f"{key}={value}")
env_file.write_text('\n'.join(out) + '\n')
PY

echo -e "${GREEN}环境变量已配置 / Environment configured${NC}"

# 6. 创建必要目录 / Create necessary directories
echo -e "\n${YELLOW}[6/10] 创建目录... / Creating directories...${NC}"
mkdir -p certbot/conf certbot/www backend/logs

# 7. 配置Nginx / Configure Nginx
echo -e "\n${YELLOW}[7/10] 配置Nginx... / Configuring Nginx...${NC}"
export WWW_DOMAIN
python3 - <<'PY'
import os
import re
from pathlib import Path

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

# 8. 启动服务 / Start services
echo -e "\n${YELLOW}[8/10] 启动服务... / Starting services...${NC}"
docker compose -f docker-compose.prod.yml up -d db redis backend

echo "等待数据库启动... / Waiting for database..."
sleep 10

# 9. 获取SSL证书 / Get SSL certificate
echo -e "\n${YELLOW}[9/10] 获取SSL证书... / Getting SSL certificate...${NC}"
if [[ -z "$CONFIGURE_SSL" ]]; then
  read -r -p "是否配置SSL? (y/n) / Configure SSL? (y/n): " CONFIGURE_SSL
fi

if [ "$CONFIGURE_SSL" = "y" ]; then
    if [[ -z "$EMAIL" ]]; then
      read -r -p "请输入邮箱地址 / Enter email address: " EMAIL
    fi

    if [[ -z "$EMAIL" ]]; then
      echo -e "${RED}邮箱不能为空 / Email cannot be empty${NC}"
      exit 1
    fi

    docker compose -f docker-compose.prod.yml up -d nginx

    CERTBOT_ARGS=(
      certonly --webroot
      --webroot-path=/var/www/certbot
      --email "$EMAIL"
      --agree-tos
      --no-eff-email
      -d "$DOMAIN"
    )
    if [[ "$WWW_DOMAIN" == "true" ]]; then
      CERTBOT_ARGS+=( -d "www.$DOMAIN" )
    fi

    docker compose -f docker-compose.prod.yml run --rm certbot "${CERTBOT_ARGS[@]}"

    docker compose -f docker-compose.prod.yml restart nginx
fi

# 10. 启动所有服务 / Start all services
echo -e "\n${YELLOW}[10/10] 启动所有服务... / Starting all services...${NC}"
docker compose -f docker-compose.prod.yml up -d

echo -e "\n${GREEN}检查服务状态... / Checking service status...${NC}"
docker compose -f docker-compose.prod.yml ps

echo -e "\n${GREEN}=================================="
echo "部署完成! / Deployment Complete!"
echo "==================================${NC}"

echo "访问您的应用 / Access your application:"
echo "  - https://$DOMAIN"
[[ -n "$SERVER_IP" ]] && echo "  - http://$SERVER_IP"
echo "  - API文档 / API Docs: https://$DOMAIN/docs"

echo "查看日志 / View logs:"
echo "  docker compose -f docker-compose.prod.yml logs -f"

echo "停止服务 / Stop services:"
echo "  docker compose -f docker-compose.prod.yml down"

echo -e "${YELLOW}重要提示 / Important Notes:${NC}"
echo "  1. 请编辑 .env 文件添加 API 密钥"
echo "  2. 配置防火墙只开放 80 和 443 端口"
echo "  3. 定期备份数据库"
