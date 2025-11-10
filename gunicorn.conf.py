# 生产环境配置
bind = "0.0.0.0:8003"
workers = 4
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 2

# 日志配置
accesslog = "/var/log/book_reader/access.log"
errorlog = "/var/log/book_reader/error.log"
loglevel = "info"

# 进程配置
daemon = False
user = "www-data"
group = "www-data"
tmp_upload_dir = None

# 安全配置
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# 重启配置
preload_app = True