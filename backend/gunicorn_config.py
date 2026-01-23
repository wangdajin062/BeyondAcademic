import multiprocessing
import os

# 绑定地址 / Bind address
bind = "0.0.0.0:8000"

# 工作进程数 / Number of workers
workers = int(os.getenv("GUNICORN_WORKERS", multiprocessing.cpu_count() * 2 + 1))

# 工作类 / Worker class
worker_class = "uvicorn.workers.UvicornWorker"

# 超时时间 / Timeout
timeout = int(os.getenv("GUNICORN_TIMEOUT", 120))

# 保持连接 / Keep alive
keepalive = 5

# 最大请求数 / Max requests
max_requests = 1000
max_requests_jitter = 50

# 日志 / Logging
accesslog = os.getenv("ACCESS_LOG", "/app/logs/access.log")
errorlog = os.getenv("ERROR_LOG", "/app/logs/error.log")
loglevel = os.getenv("LOG_LEVEL", "info")

# 进程名 / Process name
proc_name = "beyondacademic"

# 预加载应用 / Preload app
preload_app = True

# 优雅重启超时 / Graceful timeout
graceful_timeout = 30
