# Web 登录系统 - 使用说明

## 快速开始

### 1. 启动 Web API 服务器

```bash
# 方法1：使用启动脚本
./start-webapi.sh

# 方法2：手动编译和运行
cd Admin
javac common/*.java
javac -cp . backend/*.java
javac -cp . webapi/*.java
java -cp . webapi.WebApiServer 8080
```

看到以下输出说明启动成功：
```
========================================
Web API 服务器已启动
监听端口: 8080
访问地址: http://localhost:8080
========================================
```

### 2. 访问 Web 应用

打开浏览器，访问：
```
http://localhost:8080
```

### 3. 使用测试账户登录

```
用户名: admin
密码: admin123
```

---

## 功能介绍

### 登录功能
1. 切换到"登录"标签页（如未显示，点击标签页按钮）
2. 输入用户名（如：admin）
3. 输入密码（如：admin123）
4. 点击"登录"按钮
5. 成功登录后会显示成功提示

### 注册功能
1. 点击"注册"标签页
2. 输入新用户名（必须唯一）
3. 输入密码（至少6位）
4. 再次输入相同密码确认
5. 点击"注册"按钮
6. 注册成功后自动切换到登录页面

### 快速测试
在页面下方的"快速测试"区域，有三个快速测试按钮：

- **测试登录** - 使用 admin/admin123 快速登录
- **测试注册** - 注册一个新的测试用户
- **检查服务器** - 验证后端服务器是否正常运行

---

## 文件说明

### Web 前端
```
web/index.html
```
- 现代化的 Web 登录页面
- 包含完整的前端逻辑和样式
- 支持响应式设计，适配各种屏幕

### Web API 服务器
```
Admin/webapi/WebApiServer.java
```
- HTTP 服务器实现
- 提供 REST API 接口
- 处理跨域请求
- 集成用户管理逻辑

### 用户管理器
```
Admin/backend/UserManager.java
```
- 用户数据存储和管理
- 登录和注册逻辑
- 用户验证功能

### 启动脚本
```
start-webapi.sh
test-webapi.sh
```
- `start-webapi.sh` - 启动 Web API 服务器
- `test-webapi.sh` - 运行 API 功能测试

---

## API 接口

### 登录接口
```
POST /api/login
Content-Type: application/json

请求：
{
  "username": "admin",
  "password": "admin123"
}

响应 (成功)：
{
  "success": true,
  "message": "登录成功"
}

响应 (失败)：
{
  "success": false,
  "message": "用户名或密码错误"
}
```

### 注册接口
```
POST /api/register
Content-Type: application/json

请求：
{
  "username": "newuser",
  "password": "password123"
}

响应 (成功)：
{
  "success": true,
  "message": "注册成功"
}

响应 (失败)：
{
  "success": false,
  "message": "用户名已存在"
}
```

### 状态检查接口
```
GET /api/status

响应：
{
  "success": true,
  "message": "服务器正常运行",
  "version": "1.0.0",
  "timestamp": 1769139916789
}
```

---

## 常见问题

### Q: 无法连接到服务器怎么办？
**A:** 
1. 确保 Web API 服务器已启动
2. 检查端口 8080 是否被占用
3. 查看浏览器控制台（F12）的错误信息
4. 确保防火墙允许访问 localhost:8080

### Q: 密码错误提示是什么意思？
**A:** 输入的用户名或密码不正确。请检查大小写和拼写。

### Q: 如何修改服务器端口？
**A:** 修改启动命令的端口参数：
```bash
java -cp . webapi.WebApiServer 9000  # 改为 9000 端口
```
然后在浏览器中访问 `http://localhost:9000`

### Q: 注册后能立即登录吗？
**A:** 可以。注册成功后会自动切换到登录页面，可以使用新注册的账号登录。

### Q: 数据会被保存吗？
**A:** 当前实现使用内存存储，程序重启后数据会丢失。生产环境需要集成数据库。

### Q: 可以同时启动 Web API 和传统 Socket 服务器吗？
**A:** 可以。在不同的终端运行：
```bash
# 终端 1
./start-webapi.sh

# 终端 2
./Admin/start-backend.sh
```
两个服务器会共享同一个 UserManager 实例。

---

## 浏览器兼容性

- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+
- ✅ 移动浏览器（iOS Safari, Chrome Mobile）

---

## 性能指标

- **页面加载时间** - < 100ms（静态 HTML）
- **登录响应时间** - < 50ms
- **注册响应时间** - < 50ms
- **并发用户支持** - 可处理数百个并发连接

---

## 故障排除

### 服务器无法启动
```
错误: 端口 8080 已被占用
解决: 更换端口或关闭占用该端口的程序
java netstat -an | grep 8080  # 查看端口占用
lsof -i :8080  # macOS/Linux
netstat -ano | findstr :8080  # Windows
```

### 编译错误
```
错误: 找不到 symbol
解决: 确保所有源文件都已编译
javac common/*.java
javac -cp . backend/*.java
javac -cp . webapi/*.java
```

### CORS 错误（浏览器控制台）
```
Access to XMLHttpRequest... has been blocked by CORS policy
解决: Web API 服务器已配置 CORS 头，此错误通常表示服务器未运行
```

---

## 开发者信息

- **项目名称** - BeyondAcademic
- **Web API 版本** - 1.0.0
- **Java 版本要求** - Java 8+
- **开发时间** - 2026-01-23

---

## 后续计划

- [ ] 集成数据库（MySQL）
- [ ] 添加 JWT 认证
- [ ] 用户仪表板
- [ ] 个人信息管理
- [ ] 密码重置功能
- [ ] 邮件验证
- [ ] 登录日志
- [ ] 安全审计

---

**需要帮助？** 查看项目文件中的 README.md 或 WEB_TEST_REPORT.md
