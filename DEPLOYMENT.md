# 生产环境部署指南 / Production Deployment Guide

## 概述 / Overview

本指南提供BeyondAcademic系统部署到生产环境的完整步骤和最佳实践。

This guide provides complete steps and best practices for deploying the BeyondAcademic system to production.

---

## 生产环境要求 / Production Requirements

### 服务器配置 / Server Configuration

**最低配置 / Minimum Requirements:**
- CPU: 4核心 / 4 cores
- 内存 / RAM: 8GB
- 存储 / Storage: 50GB SSD
- 操作系统 / OS: Ubuntu 20.04 LTS 或更高 / Ubuntu 20.04 LTS or higher

**推荐配置 / Recommended:**
- CPU: 8核心 / 8 cores
- 内存 / RAM: 16GB
- 存储 / Storage: 100GB SSD
- 操作系统 / OS: Ubuntu 22.04 LTS

### 依赖服务 / Required Services

1. **PostgreSQL 14+** - 数据库 / Database
2. **Redis 6+** - 缓存 / Cache (可选 / Optional)
3. **Nginx** - 反向代理 / Reverse Proxy
4. **Let's Encrypt** - SSL证书 / SSL Certificates

---

## 部署步骤 / Deployment Steps

### 第一步：准备服务器 / Step 1: Prepare Server

```bash
# 更新系统 / Update system
sudo apt update && sudo apt upgrade -y

# 安装必要软件 / Install required software
sudo apt install -y python3.11 python3.11-venv python3-pip postgresql postgresql-contrib nginx certbot python3-certbot-nginx git redis-server

# 启动服务 / Start services
sudo systemctl start postgresql
sudo systemctl enable postgresql
sudo systemctl start redis
sudo systemctl enable redis
```

### 第二步：配置数据库 / Step 2: Configure Database

```bash
# 切换到postgres用户 / Switch to postgres user
sudo -u postgres psql

# 在PostgreSQL中执行 / Execute in PostgreSQL:
CREATE DATABASE beyondacademic;
CREATE USER beyondacademic_user WITH PASSWORD 'your_secure_password_here';
GRANT ALL PRIVILEGES ON DATABASE beyondacademic TO beyondacademic_user;
\q
```

### 第三步：克隆和配置应用 / Step 3: Clone and Configure Application

```bash
# 创建应用目录 / Create application directory
sudo mkdir -p /var/www/beyondacademic
sudo chown $USER:$USER /var/www/beyondacademic
cd /var/www/beyondacademic

# 克隆代码 / Clone code
git clone https://github.com/wangdajin062/BeyondAcademic.git .
git checkout copilot/add-article-management-module

# 创建环境变量文件 / Create environment file
cp config/.env.example .env
```

### 第四步：配置环境变量 / Step 4: Configure Environment Variables

编辑 `.env` 文件 / Edit `.env` file:

```bash
# 数据库配置 / Database Configuration
DATABASE_URL=postgresql://beyondacademic_user:your_secure_password_here@localhost/beyondacademic

# API配置 / API Configuration
API_HOST=0.0.0.0
API_PORT=8000
SECRET_KEY=your_very_long_random_secret_key_here_minimum_32_characters

# 跨域配置 / CORS Configuration
ALLOWED_ORIGINS=https://yourdomain.com

# AI服务密钥 / AI Service Keys (如果使用 / if using)
OPENAI_API_KEY=your_openai_api_key_here
SEMANTIC_SCHOLAR_API_KEY=your_semantic_scholar_key_here

# 日志级别 / Log Level
LOG_LEVEL=INFO

# 生产环境标记 / Production Flag
ENVIRONMENT=production
```

### 第五步：安装后端依赖 / Step 5: Install Backend Dependencies

```bash
cd /var/www/beyondacademic/backend

# 创建虚拟环境 / Create virtual environment
python3.11 -m venv venv

# 激活虚拟环境 / Activate virtual environment
source venv/bin/activate

# 安装依赖 / Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 安装生产环境额外依赖 / Install production extras
pip install gunicorn psycopg2-binary
```

### 第六步：数据库迁移 / Step 6: Database Migration

创建数据库迁移脚本 / Create database migration script:

```bash
# 创建迁移脚本 / Create migration script
nano /var/www/beyondacademic/backend/migrations/init.sql
```

添加SQL内容 / Add SQL content:

```sql
-- 文章表 / Articles table
CREATE TABLE IF NOT EXISTS articles (
    article_id UUID PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    abstract TEXT,
    content TEXT NOT NULL,
    status VARCHAR(50) NOT NULL,
    template VARCHAR(50) NOT NULL,
    authors TEXT[] DEFAULT '{}',
    keywords TEXT[] DEFAULT '{}',
    references TEXT[] DEFAULT '{}',
    current_version INTEGER DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    submitted_at TIMESTAMP WITH TIME ZONE,
    published_at TIMESTAMP WITH TIME ZONE
);

-- 版本表 / Versions table
CREATE TABLE IF NOT EXISTS article_versions (
    version_id UUID PRIMARY KEY,
    article_id UUID REFERENCES articles(article_id) ON DELETE CASCADE,
    version_number INTEGER NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    changes_summary TEXT,
    author VARCHAR(255) NOT NULL,
    UNIQUE(article_id, version_number)
);

-- 索引 / Indexes
CREATE INDEX IF NOT EXISTS idx_articles_status ON articles(status);
CREATE INDEX IF NOT EXISTS idx_articles_created_at ON articles(created_at);
CREATE INDEX IF NOT EXISTS idx_article_versions_article_id ON article_versions(article_id);
```

执行迁移 / Execute migration:

```bash
sudo -u postgres psql beyondacademic < /var/www/beyondacademic/backend/migrations/init.sql
```

### 第七步：配置Gunicorn / Step 7: Configure Gunicorn

创建Gunicorn配置 / Create Gunicorn configuration:

```bash
nano /var/www/beyondacademic/backend/gunicorn_config.py
```

```python
import multiprocessing

# 绑定地址 / Bind address
bind = "127.0.0.1:8000"

# 工作进程数 / Number of workers
workers = multiprocessing.cpu_count() * 2 + 1

# 工作类 / Worker class
worker_class = "uvicorn.workers.UvicornWorker"

# 超时时间 / Timeout
timeout = 120

# 日志 / Logging
accesslog = "/var/log/beyondacademic/access.log"
errorlog = "/var/log/beyondacademic/error.log"
loglevel = "info"

# 进程名 / Process name
proc_name = "beyondacademic"
```

创建日志目录 / Create log directory:

```bash
sudo mkdir -p /var/log/beyondacademic
sudo chown $USER:$USER /var/log/beyondacademic
```

### 第八步：创建系统服务 / Step 8: Create System Service

```bash
sudo nano /etc/systemd/system/beyondacademic.service
```

```ini
[Unit]
Description=BeyondAcademic API Service
After=network.target postgresql.service

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/var/www/beyondacademic/backend
Environment="PATH=/var/www/beyondacademic/backend/venv/bin"
EnvironmentFile=/var/www/beyondacademic/.env
ExecStart=/var/www/beyondacademic/backend/venv/bin/gunicorn -c gunicorn_config.py main:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启动服务 / Start service:

```bash
# 设置权限 / Set permissions
sudo chown -R www-data:www-data /var/www/beyondacademic
sudo chmod -R 755 /var/www/beyondacademic

# 重载systemd / Reload systemd
sudo systemctl daemon-reload

# 启动服务 / Start service
sudo systemctl start beyondacademic

# 设置开机启动 / Enable on boot
sudo systemctl enable beyondacademic

# 检查状态 / Check status
sudo systemctl status beyondacademic
```

### 第九步：配置Nginx / Step 9: Configure Nginx

```bash
sudo nano /etc/nginx/sites-available/beyondacademic
```

```nginx
# 限流配置 / Rate limiting
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;

upstream beyondacademic_backend {
    server 127.0.0.1:8000 fail_timeout=0;
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    # 重定向到HTTPS / Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL证书配置 (Let's Encrypt会自动配置)
    # SSL certificate config (Let's Encrypt will auto-configure)
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    # SSL安全配置 / SSL security config
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    # 安全头 / Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # 日志 / Logs
    access_log /var/log/nginx/beyondacademic_access.log;
    error_log /var/log/nginx/beyondacademic_error.log;
    
    # 最大上传大小 / Max upload size
    client_max_body_size 50M;
    
    # API代理 / API proxy
    location /api {
        limit_req zone=api_limit burst=20 nodelay;
        
        proxy_pass http://beyondacademic_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 超时设置 / Timeout settings
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # API文档 / API docs
    location /docs {
        proxy_pass http://beyondacademic_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    # 健康检查 / Health check
    location /health {
        proxy_pass http://beyondacademic_backend;
        access_log off;
    }
    
    # 静态文件 (前端) / Static files (frontend)
    location / {
        root /var/www/beyondacademic/frontend/build;
        try_files $uri $uri/ /index.html;
    }
}
```

启用站点 / Enable site:

```bash
# 创建符号链接 / Create symbolic link
sudo ln -s /etc/nginx/sites-available/beyondacademic /etc/nginx/sites-enabled/

# 测试配置 / Test configuration
sudo nginx -t

# 重启Nginx / Restart Nginx
sudo systemctl restart nginx
```

### 第十步：配置SSL证书 / Step 10: Configure SSL Certificate

```bash
# 获取Let's Encrypt证书 / Get Let's Encrypt certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# 测试自动续期 / Test auto-renewal
sudo certbot renew --dry-run
```

### 第十一步：前端构建和部署 / Step 11: Frontend Build and Deploy

```bash
cd /var/www/beyondacademic/frontend

# 安装Node.js 18+ (如未安装) / Install Node.js 18+ (if not installed)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# 安装依赖 / Install dependencies
npm install

# 构建生产版本 / Build for production
npm run build

# 设置权限 / Set permissions
sudo chown -R www-data:www-data build/
```

---

## 安全加固 / Security Hardening

### 1. 防火墙配置 / Firewall Configuration

```bash
# 启用UFW / Enable UFW
sudo ufw enable

# 允许SSH / Allow SSH
sudo ufw allow 22/tcp

# 允许HTTP/HTTPS / Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# 检查状态 / Check status
sudo ufw status
```

### 2. 配置认证 / Configure Authentication

需要实现JWT认证。修改 `backend/main.py` 添加认证中间件：

Need to implement JWT authentication. Modify `backend/main.py` to add auth middleware:

```python
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from datetime import datetime, timedelta

# JWT配置 / JWT configuration
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """验证JWT令牌 / Validate JWT token"""
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        return username
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

# 在路由中使用 / Use in routes:
# @router.post("/articles/", dependencies=[Depends(get_current_user)])
```

### 3. 设置备份 / Setup Backups

```bash
# 创建备份脚本 / Create backup script
sudo nano /usr/local/bin/backup_beyondacademic.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/var/backups/beyondacademic"
DATE=$(date +%Y%m%d_%H%M%S)

# 创建备份目录 / Create backup directory
mkdir -p $BACKUP_DIR

# 备份数据库 / Backup database
sudo -u postgres pg_dump beyondacademic | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# 备份文件 / Backup files
tar -czf $BACKUP_DIR/files_$DATE.tar.gz /var/www/beyondacademic

# 删除7天前的备份 / Delete backups older than 7 days
find $BACKUP_DIR -type f -mtime +7 -delete

echo "Backup completed: $DATE"
```

```bash
# 设置权限 / Set permissions
sudo chmod +x /usr/local/bin/backup_beyondacademic.sh

# 添加到crontab (每天凌晨2点备份) / Add to crontab (backup at 2 AM daily)
sudo crontab -e
# 添加: 0 2 * * * /usr/local/bin/backup_beyondacademic.sh
```

---

## 监控和维护 / Monitoring and Maintenance

### 1. 日志监控 / Log Monitoring

```bash
# 查看应用日志 / View application logs
sudo journalctl -u beyondacademic -f

# 查看Nginx日志 / View Nginx logs
sudo tail -f /var/log/nginx/beyondacademic_access.log
sudo tail -f /var/log/nginx/beyondacademic_error.log
```

### 2. 性能监控 / Performance Monitoring

安装监控工具 / Install monitoring tools:

```bash
# 安装监控工具 / Install monitoring tools
sudo apt install -y htop iotop nethogs

# 实时监控 / Real-time monitoring
htop                    # CPU和内存 / CPU and memory
sudo iotop             # 磁盘I/O / Disk I/O
sudo nethogs           # 网络流量 / Network traffic
```

### 3. 健康检查 / Health Checks

设置健康检查脚本 / Setup health check script:

```bash
nano /usr/local/bin/health_check.sh
```

```bash
#!/bin/bash
HEALTH_URL="https://yourdomain.com/health"
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" $HEALTH_URL)

if [ $RESPONSE -eq 200 ]; then
    echo "$(date): Service is healthy"
else
    echo "$(date): Service is unhealthy (HTTP $RESPONSE)"
    # 重启服务 / Restart service
    sudo systemctl restart beyondacademic
fi
```

```bash
chmod +x /usr/local/bin/health_check.sh

# 每5分钟检查一次 / Check every 5 minutes
sudo crontab -e
# 添加: */5 * * * * /usr/local/bin/health_check.sh >> /var/log/health_check.log 2>&1
```

---

## 性能优化 / Performance Optimization

### 1. 配置Redis缓存 / Configure Redis Cache

在 `backend/main.py` 中添加缓存 / Add caching in `backend/main.py`:

```python
import redis
import json
from functools import wraps

# Redis连接 / Redis connection
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

def cache_result(expiration=300):
    """缓存装饰器 / Cache decorator"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            cached = redis_client.get(cache_key)
            
            if cached:
                return json.loads(cached)
            
            result = await func(*args, **kwargs)
            redis_client.setex(cache_key, expiration, json.dumps(result))
            return result
        return wrapper
    return decorator
```

### 2. 数据库连接池 / Database Connection Pool

更新 `backend/services/article_service.py` 使用数据库连接池：

Update `backend/services/article_service.py` to use database connection pool:

```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool
import os

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=0,
    pool_pre_ping=True
)
```

---

## 故障排除 / Troubleshooting

### 常见问题 / Common Issues

**1. 服务无法启动 / Service won't start**

```bash
# 检查日志 / Check logs
sudo journalctl -u beyondacademic -n 50

# 检查端口占用 / Check port usage
sudo netstat -tlnp | grep 8000

# 手动测试 / Manual test
cd /var/www/beyondacademic/backend
source venv/bin/activate
python main.py
```

**2. 数据库连接失败 / Database connection fails**

```bash
# 检查PostgreSQL状态 / Check PostgreSQL status
sudo systemctl status postgresql

# 测试连接 / Test connection
sudo -u postgres psql beyondacademic -c "SELECT version();"
```

**3. Nginx 502错误 / Nginx 502 error**

```bash
# 检查后端是否运行 / Check if backend is running
sudo systemctl status beyondacademic

# 检查Nginx错误日志 / Check Nginx error log
sudo tail -f /var/log/nginx/beyondacademic_error.log
```

---

## 更新和维护 / Updates and Maintenance

### 应用更新 / Application Updates

```bash
cd /var/www/beyondacademic

# 拉取最新代码 / Pull latest code
git pull origin main

# 更新后端依赖 / Update backend dependencies
cd backend
source venv/bin/activate
pip install -r requirements.txt

# 重新构建前端 / Rebuild frontend
cd ../frontend
npm install
npm run build

# 重启服务 / Restart services
sudo systemctl restart beyondacademic
sudo systemctl reload nginx
```

### 依赖更新 / Dependency Updates

```bash
# 检查过期的包 / Check outdated packages
pip list --outdated

# 更新特定包 / Update specific package
pip install --upgrade package_name

# 运行安全检查 / Run security check
pip install safety
safety check
```

---

## 检查清单 / Checklist

部署前检查 / Pre-deployment checklist:

- [ ] 服务器配置满足要求 / Server meets requirements
- [ ] PostgreSQL已安装和配置 / PostgreSQL installed and configured
- [ ] 环境变量已正确设置 / Environment variables set correctly
- [ ] 所有依赖已安装 / All dependencies installed
- [ ] 数据库迁移已执行 / Database migrations executed
- [ ] SSL证书已配置 / SSL certificate configured
- [ ] 防火墙规则已设置 / Firewall rules set
- [ ] 备份脚本已配置 / Backup script configured
- [ ] 监控和日志已设置 / Monitoring and logging set up
- [ ] 健康检查脚本已配置 / Health check script configured
- [ ] 所有服务已启动并运行 / All services started and running
- [ ] API可访问并返回正确响应 / API accessible and returning correct responses

---

## 支持和帮助 / Support and Help

如遇到问题，请检查：

If you encounter issues, please check:

1. 系统日志 / System logs: `sudo journalctl -u beyondacademic`
2. 应用日志 / Application logs: `/var/log/beyondacademic/`
3. Nginx日志 / Nginx logs: `/var/log/nginx/`
4. 数据库日志 / Database logs: `/var/log/postgresql/`

---

## 总结 / Summary

本指南涵盖了从零开始部署BeyondAcademic到生产环境的所有步骤。请按照步骤仔细执行，确保每一步都正确完成。

This guide covers all steps to deploy BeyondAcademic to production from scratch. Please follow the steps carefully and ensure each step is completed correctly.

**重要提示 / Important Notes:**
- 定期更新系统和依赖 / Regularly update system and dependencies
- 监控系统性能和日志 / Monitor system performance and logs
- 定期备份数据 / Regularly backup data
- 保持安全最佳实践 / Follow security best practices

祝部署顺利！/ Good luck with deployment!
