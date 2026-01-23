#!/bin/bash
# BeyondAcademic生产环境快速部署脚本 / Quick Production Deployment Script

set -e

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
   echo "请使用: sudo $0"
   exit 1
fi

# 获取域名 / Get domain name
read -p "请输入您的域名 (例如: example.com) / Enter your domain (e.g., example.com): " DOMAIN

if [ -z "$DOMAIN" ]; then
    echo -e "${RED}域名不能为空 / Domain cannot be empty${NC}"
    exit 1
fi

echo -e "${GREEN}使用域名 / Using domain: $DOMAIN${NC}"

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
if ! command -v docker compose &> /dev/null; then
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
    git pull
fi

# 5. 配置环境变量 / Configure environment
echo -e "\n${YELLOW}[5/10] 配置环境变量... / Configuring environment...${NC}"
if [ ! -f ".env" ]; then
    cp .env.production .env
    
    # 生成密钥 / Generate secret key
    SECRET_KEY=$(openssl rand -hex 32)
    DB_PASSWORD=$(openssl rand -hex 16)
    
    # 更新.env文件 / Update .env file
    sed -i "s/your_very_secure_database_password_here_min_16_chars/$DB_PASSWORD/g" .env
    sed -i "s/your_secret_key_here_must_be_at_least_32_characters_long_and_random/$SECRET_KEY/g" .env
    sed -i "s/yourdomain.com/$DOMAIN/g" .env
    
    echo -e "${GREEN}环境变量已配置 / Environment configured${NC}"
    echo -e "${YELLOW}请编辑 .env 文件添加其他必要配置 / Please edit .env file to add other necessary configurations${NC}"
else
    echo ".env文件已存在，跳过 / .env file exists, skipping"
fi

# 6. 创建必要目录 / Create necessary directories
echo -e "\n${YELLOW}[6/10] 创建目录... / Creating directories...${NC}"
mkdir -p certbot/conf certbot/www backend/logs

# 7. 配置Nginx / Configure Nginx
echo -e "\n${YELLOW}[7/10] 配置Nginx... / Configuring Nginx...${NC}"
sed -i "s/yourdomain.com/$DOMAIN/g" nginx/conf.d/beyondacademic.conf

# 8. 启动服务 / Start services
echo -e "\n${YELLOW}[8/10] 启动服务... / Starting services...${NC}"
docker compose -f docker-compose.prod.yml up -d db redis backend

# 等待数据库就绪 / Wait for database
echo "等待数据库启动... / Waiting for database..."
sleep 10

# 9. 获取SSL证书 / Get SSL certificate
echo -e "\n${YELLOW}[9/10] 获取SSL证书... / Getting SSL certificate...${NC}"
read -p "是否配置SSL? (y/n) / Configure SSL? (y/n): " CONFIGURE_SSL

if [ "$CONFIGURE_SSL" = "y" ]; then
    read -p "请输入邮箱地址 / Enter email address: " EMAIL
    
    # 首次获取证书需要临时启动Nginx / First-time cert requires temporary Nginx
    docker compose -f docker-compose.prod.yml up -d nginx
    
    # 运行certbot / Run certbot
    docker compose -f docker-compose.prod.yml run --rm certbot certonly --webroot \
        --webroot-path=/var/www/certbot \
        --email $EMAIL \
        --agree-tos \
        --no-eff-email \
        -d $DOMAIN -d www.$DOMAIN
    
    # 重启Nginx以应用证书 / Restart Nginx to apply certificate
    docker compose -f docker-compose.prod.yml restart nginx
fi

# 10. 启动所有服务 / Start all services
echo -e "\n${YELLOW}[10/10] 启动所有服务... / Starting all services...${NC}"
docker compose -f docker-compose.prod.yml up -d

# 检查服务状态 / Check service status
echo -e "\n${GREEN}检查服务状态... / Checking service status...${NC}"
docker compose -f docker-compose.prod.yml ps

# 完成 / Done
echo -e "\n${GREEN}=================================="
echo "部署完成! / Deployment Complete!"
echo "==================================${NC}"
echo ""
echo "访问您的应用 / Access your application:"
echo "  - https://$DOMAIN"
echo "  - API文档 / API Docs: https://$DOMAIN/docs"
echo ""
echo "查看日志 / View logs:"
echo "  docker compose -f docker-compose.prod.yml logs -f"
echo ""
echo "停止服务 / Stop services:"
echo "  docker compose -f docker-compose.prod.yml down"
echo ""
echo -e "${YELLOW}重要提示 / Important Notes:${NC}"
echo "  1. 请编辑 .env 文件添加 API 密钥"
echo "  2. 配置防火墙只开放 80 和 443 端口"
echo "  3. 定期备份数据库"
echo ""
