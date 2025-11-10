# 🚀 随机阅读电子书应用部署指南

## 📋 目录
- [快速开始](#快速开始)
- [环境要求](#环境要求)
- [Docker部署](#docker部署)
- [手动部署](#手动部署)
- [配置说明](#配置说明)
- [故障排除](#故障排除)
- [监控和维护](#监控和维护)

## ⚡ 快速开始

### 1. 使用自动化脚本（推荐）
```bash
# 克隆项目
git clone <repository-url>
cd book-reader-app

# 运行部署脚本
chmod +x scripts/start.sh
./scripts/start.sh
```

### 2. 使用Docker Compose
```bash
# 复制环境配置
cp .env.example .env

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f
```

## 📦 环境要求

### Docker部署
- Docker 20.10+
- Docker Compose 2.0+
- 至少2GB可用内存
- 至少5GB可用磁盘空间

### 手动部署
- Python 3.8+
- SQLite 3.x
- 2GB+ 内存

## 🐳 Docker部署

### 1. 基础部署
```bash
# 构建镜像
docker build -t book-reader-app .

# 运行容器
docker run -d \
  --name book-reader-app \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/app/static/uploads:/app/app/static/uploads \
  -e SECRET_KEY="your-secret-key" \
  book-reader-app
```

### 2. Docker Compose部署

#### 开发环境
```bash
docker-compose up -d
```

#### 生产环境（带Nginx）
```bash
docker-compose --profile with-nginx up -d
```

#### 高可用部署（带Redis缓存）
```bash
docker-compose --profile with-redis --profile with-nginx up -d
```

### 3. 环境变量配置
创建 `.env` 文件：
```env
# 应用配置
ENV=production
HOST=0.0.0.0
PORT=8000

# 安全配置
SECRET_KEY=your-super-secret-key-change-this-in-production-please
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# 数据库配置
DATABASE_URL=sqlite:///./data/book_reader.db

# 文件上传配置
MAX_FILE_SIZE=10485760
ALLOWED_EXTENSIONS=jpg,jpeg,png,gif,webp

# CORS配置
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080

# 日志配置
LOG_LEVEL=info
```

## 🔧 手动部署

### 1. 环境准备
```bash
# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境
```bash
# 复制环境配置
cp .env.example .env

# 编辑配置文件
nano .env
```

### 3. 数据库初始化
```bash
# 创建必要目录
mkdir -p data app/static/uploads app/logs

# 初始化数据库（应用启动时自动执行）
```

### 4. 启动应用
```bash
# 开发环境
python main.py

# 生产环境
gunicorn -c gunicorn.conf.py main:app
```

## ⚙️ 配置说明

### 环境变量详解

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `ENV` | development | 运行环境 (development/production) |
| `HOST` | 0.0.0.0 | 监听地址 |
| `PORT` | 8000 | 监听端口 |
| `SECRET_KEY` | - | JWT密钥，生产环境必须更改 |
| `DATABASE_URL` | sqlite:///./book_reader.db | 数据库连接URL |
| `MAX_FILE_SIZE` | 10485760 | 最大文件上传大小（字节） |
| `ALLOWED_EXTENSIONS` | jpg,jpeg,png,gif,webp | 允许的文件扩展名 |
| `LOG_LEVEL` | info | 日志级别 |

### Nginx配置（可选）
如果使用Nginx反向代理，配置文件 `nginx.conf` 包含：
- Gzip压缩
- 静态文件缓存
- 安全头设置
- 请求大小限制

### SSL/HTTPS配置
1. 将SSL证书放入 `ssl/` 目录
2. 修改 `nginx.conf` 添加SSL配置
3. 重启Nginx服务

## 🔍 故障排除

### 常见问题

#### 1. 容器启动失败
```bash
# 查看容器日志
docker-compose logs app

# 检查容器状态
docker-compose ps
```

#### 2. 数据库连接错误
```bash
# 检查数据目录权限
ls -la data/

# 重新初始化数据库
rm -f data/*.db
docker-compose restart app
```

#### 3. 文件上传失败
```bash
# 检查上传目录权限
ls -la app/static/uploads/

# 检查文件大小限制
grep MAX_FILE_SIZE .env
```

#### 4. 权限问题
```bash
# 修复文件权限
sudo chown -R $USER:$USER .
chmod -R 755 app/static/uploads
```

### 日志查看
```bash
# Docker环境
docker-compose logs -f app

# 手动部署
tail -f app/logs/app.log
```

### 性能监控
```bash
# 检查容器资源使用
docker stats

# 检查磁盘使用
df -h
```

## 📊 监控和维护

### 健康检查
应用提供以下健康检查端点：
- `GET /health` - 基本健康检查
- `GET /api/auth/me` - 认证服务检查

### 数据备份
```bash
# 备份数据库
cp data/book_reader.db backup/book_reader_$(date +%Y%m%d).db

# 备份上传文件
tar -czf backup/uploads_$(date +%Y%m%d).tar.gz app/static/uploads/
```

### 日志轮转
建议配置日志轮转以防止日志文件过大：
```bash
# 添加到 crontab
0 0 * * * find app/logs -name "*.log" -mtime +7 -delete
```

### 更新部署
```bash
# 拉取最新代码
git pull

# 重新构建和部署
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## 🔒 安全建议

1. **更改默认密钥**：生产环境必须更改 `SECRET_KEY`
2. **使用HTTPS**：配置SSL证书启用HTTPS
3. **限制CORS**：设置 `ALLOWED_ORIGINS` 为具体域名
4. **定期备份**：定期备份数据库和上传文件
5. **监控日志**：定期检查应用和访问日志
6. **更新依赖**：定期更新Python依赖和基础镜像

## 📞 支持

如果遇到问题，请：
1. 查看日志文件确定错误原因
2. 检查配置文件是否正确
3. 确认环境要求已满足
4. 参考故障排除部分

---

**部署完成后，访问 http://localhost:8000 开始使用应用！**