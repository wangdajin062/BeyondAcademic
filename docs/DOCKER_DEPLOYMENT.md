# Docker生产部署 / Docker Production Deployment

## 概述 / Overview

使用Docker和Docker Compose快速部署BeyondAcademic到生产环境。

Quick production deployment of BeyondAcademic using Docker and Docker Compose.

---

## 前置要求 / Prerequisites

```bash
# 安装Docker / Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 安装Docker Compose / Install Docker Compose
sudo apt install docker-compose-plugin

# 验证安装 / Verify installation
docker --version
docker compose version
```

---

## 快速开始 / Quick Start

```bash
# 克隆仓库 / Clone repository
git clone https://github.com/wangdajin062/BeyondAcademic.git
cd BeyondAcademic

# 配置环境变量 / Configure environment
cp .env.example .env
# 编辑.env文件设置密钥和配置 / Edit .env to set keys and config

# 启动所有服务 / Start all services
docker compose -f docker-compose.prod.yml up -d

# 查看日志 / View logs
docker compose -f docker-compose.prod.yml logs -f
```

访问应用 / Access application: `https://yourdomain.com`

---

## 停止和管理 / Stop and Manage

```bash
# 停止服务 / Stop services
docker compose -f docker-compose.prod.yml down

# 重启服务 / Restart services
docker compose -f docker-compose.prod.yml restart

# 查看状态 / View status
docker compose -f docker-compose.prod.yml ps

# 更新应用 / Update application
git pull
docker compose -f docker-compose.prod.yml up -d --build
```
