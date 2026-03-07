# 阿里云 ECS 部署指南（BeyondAcademic）

本文档用于将 BeyondAcademic 部署到阿里云 ECS（Ubuntu 22.04），并验证核心功能可用。

## 1. 资源准备

- ECS（建议 4C8G 及以上）
- 安全组开放端口：`22`、`80`、`443`
- 域名已解析到 ECS 公网 IP（A 记录）

## 2. 安装 Docker 环境

```bash
sudo apt update
sudo apt install -y ca-certificates curl gnupg git
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo $VERSION_CODENAME) stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo usermod -aG docker $USER
newgrp docker
```

## 3. 一键部署脚本

仓库新增了阿里云部署脚本：`scripts/deploy_aliyun_ecs.sh`。

```bash
git clone https://github.com/wangdajin062/BeyondAcademic.git
cd BeyondAcademic

DOMAIN=your-domain.com \
EMAIL=ops@your-domain.com \
BRANCH=main \
ENABLE_TEST_AUTH=false \
WWW_DOMAIN=true \
./scripts/deploy_aliyun_ecs.sh
```

### 可选环境变量

- `APP_DIR`：默认 `/opt/BeyondAcademic`
- `DB_PASSWORD`：不传则自动生成
- `SECRET_KEY`：不传则自动生成
- `OPENAI_API_KEY`：使用 AI 能力时传入
- `ALLOWED_ORIGINS`：默认 `https://$DOMAIN`
- `ENABLE_TEST_AUTH`：默认 `false`（生产强烈建议保持关闭）
- `WWW_DOMAIN`：默认 `true`，如无 `www` 解析可设为 `false`


### 指定你的部署参数（haerb.org.cn / 8.155.168.97）

```bash
DOMAIN=haerb.org.cn \
SERVER_IP=8.155.168.97 \
EMAIL=ops@haerb.org.cn \
BRANCH=main \
ENABLE_TEST_AUTH=false \
WWW_DOMAIN=false \
./scripts/deploy_aliyun_ecs.sh
```

如果你坚持用一行远程脚本方式：

```bash
curl -fsSL https://raw.githubusercontent.com/wangdajin062/BeyondAcademic/main/deploy.sh | \
  sudo DOMAIN=haerb.org.cn SERVER_IP=8.155.168.97 CONFIGURE_SSL=y EMAIL=ops@haerb.org.cn WWW_DOMAIN=false bash
```

## 4. 部署后验证

```bash
cd /opt/BeyondAcademic
docker compose -f docker-compose.prod.yml ps
curl -I https://your-domain.com/health
curl -I https://your-domain.com/docs
```

## 5. 功能验证清单（建议）

1. 文章创建 / 更新 / 版本历史
2. 语法检查与格式建议
3. 推荐检索与句子优化
4. 登录测试页（如启用测试登录）

## 6. 生产安全建议

- `ENABLE_TEST_AUTH=false`
- 更换默认测试账号（或完全禁用测试登录）
- 启用阿里云 WAF 与主机安全
- 配置快照与异地备份
- 定期轮换密钥（`SECRET_KEY`、数据库口令、API Key）
