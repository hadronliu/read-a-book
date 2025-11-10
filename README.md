# 📚 随机阅读电子书应用

一个现代化的随机阅读电子书管理应用，使用 FastAPI + SQLite 构建，支持用户注册、登录、书籍管理和阅读时长记录。

## ✨ 功能特性

### 📖 核心功能
- **用户认证系统** - 注册、登录、JWT token认证
- **书籍管理** - 添加、编辑、删除、查看书籍
- **封面上传** - 支持图片封面上传和预览
- **随机阅读** - 随机选择一本书开始阅读
- **阅读计时** - 精确记录每本书的阅读时长
- **数据统计** - 查看阅读时长统计和历史记录

### 🛠️ 技术特性
- **现代化架构** - FastAPI + SQLAlchemy + Pydantic
- **RESTful API** - 完整的 REST API 支持
- **响应式前端** - 现代化的用户界面
- **数据库迁移** - 自动创建和管理数据库表
- **文件上传** - 安全的文件上传处理
- **错误处理** - 完善的错误处理和日志记录
- **Docker支持** - 完整的容器化部署方案

## 🚀 快速开始

### 方式一：本地开发
```bash
# 1. 克隆项目
git clone <repository-url>
cd book-reader-app

# 2. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境变量
cp .env.example .env
# 编辑 .env 文件设置必要的配置

# 5. 启动应用
python main.py
```

### 方式二：Docker部署（推荐）
```bash
# 1. 使用自动化脚本
chmod +x scripts/start.sh
./scripts/start.sh

# 2. 或手动部署
docker-compose up -d
```

### 方式三：生产环境部署
```bash
# 使用Nginx反向代理
docker-compose --profile with-nginx up -d

# 使用Redis缓存
docker-compose --profile with-redis --profile with-nginx up -d
```

## 📱 访问应用

启动后访问：
- **主应用**: http://localhost:8000
- **API文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/health

## 📁 项目结构

```
book-reader-app/
├── app/                    # 应用主目录
│   ├── api/               # API路由
│   │   └── routes.py      # REST API定义
│   ├── models/            # 数据模型
│   │   └── book.py        # 数据库模型
│   ├── schemas/           # 数据验证
│   │   └── book.py        # Pydantic模型
│   ├── services/          # 业务逻辑
│   │   ├── auth.py        # 认证服务
│   │   └── book_service.py # 书籍服务
│   ├── templates/         # HTML模板
│   │   └── index.html     # 主页面
│   ├── static/            # 静态文件
│   │   └── uploads/       # 上传文件目录
│   ├── database.py        # 数据库配置
│   └── main.py           # 应用入口
├── scripts/              # 部署脚本
│   └── start.sh          # 自动化部署脚本
├── docker-compose.yml    # Docker编排
├── Dockerfile           # Docker镜像
├── nginx.conf           # Nginx配置
├── requirements.txt     # Python依赖
├── .env.example        # 环境变量示例
└── README.md           # 项目文档
```

## ⚙️ 配置说明

### 环境变量
创建 `.env` 文件并配置以下变量：

```env
# 应用配置
ENV=development
HOST=0.0.0.0
PORT=8000

# 数据库配置
DATABASE_URL=sqlite:///./book_reader.db

# 安全配置
SECRET_KEY=your-super-secret-key-change-this-in-production-please
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# 文件上传配置
MAX_FILE_SIZE=10485760
ALLOWED_EXTENSIONS=jpg,jpeg,png,gif,webp

# 日志配置
LOG_LEVEL=info
```

## 🔧 开发指南

### API文档
启动应用后访问 http://localhost:8000/docs 查看完整的API文档。

### 数据库管理
项目包含 `db_manager.py` 脚本用于数据库管理：

```bash
# 查看所有数据
python db_manager.py list

# 查看用户列表
python db_manager.py users

# 查看书籍列表
python db_manager.py books

# 添加用户
python db_manager.py add-user <username> [email]

# 添加书籍
python db_manager.py add-book <title> <owner_id> [description]

# 备份数据库
python db_manager.py backup
```

### 日志调试
```bash
# 查看应用日志
tail -f app/logs/app.log

# Docker环境日志
docker-compose logs -f app
```

## 🐳 Docker部署详解

### 基础部署
```bash
# 构建镜像
docker build -t book-reader-app .

# 运行容器
docker run -d \
  --name book-reader-app \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -e SECRET_KEY="your-secret-key" \
  book-reader-app
```

### 生产环境部署
```bash
# 完整的生产环境部署
docker-compose --profile with-nginx up -d
```

包含：
- **Nginx反向代理** - 处理静态文件和负载均衡
- **Redis缓存** - 提高应用性能
- **SSL支持** - HTTPS安全访问
- **健康检查** - 自动监控应用状态

## 🔒 安全特性

- **JWT认证** - 安全的用户认证机制
- **密码加密** - bcrypt哈希加密
- **CORS保护** - 跨域请求保护
- **文件验证** - 上传文件类型和大小限制
- **SQL注入防护** - SQLAlchemy ORM保护
- **安全头** - HTTP安全头设置

## 🧪 测试

### 手动测试
1. 访问 http://localhost:8000
2. 注册新用户
3. 登录系统
4. 添加书籍
5. 开始阅读计时

### API测试
```bash
# 健康检查
curl http://localhost:8000/health

# 用户注册
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"test123","email":"test@example.com"}'

# 用户登录
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"test123"}'
```

## 📊 性能优化

- **数据库优化** - 索引优化和连接池配置
- **静态文件缓存** - Nginx静态文件缓存
- **Gzip压缩** - 响应数据压缩
- **异步处理** - FastAPI异步特性
- **Redis缓存** - 可选的Redis缓存支持

## 🚨 故障排除

### 常见问题

#### 1. 应用启动失败
```bash
# 检查日志
python main.py  # 查看详细错误信息

# 检查数据库连接
python -c "from app.database import test_db_connection; print(test_db_connection())"
```

#### 2. 注册功能问题
- 检查用户名是否已存在
- 确认密码符合要求（至少6位，包含字母和数字）
- 查看浏览器控制台错误信息

#### 3. 文件上传失败
- 检查文件大小是否超过限制（默认10MB）
- 确认文件类型是否被允许
- 检查上传目录权限

#### 4. Docker部署问题
```bash
# 查看容器日志
docker-compose logs app

# 重新构建镜像
docker-compose build --no-cache

# 检查容器状态
docker-compose ps
```

## 📈 监控和维护

### 健康检查
应用提供多个健康检查端点：
- `/health` - 基本应用状态
- `/api/auth/me` - 认证服务状态

### 日志管理
```bash
# 设置日志轮转
0 0 * * * find app/logs -name "*.log" -mtime +7 -delete

# 查看实时日志
tail -f app/logs/app.log
```

### 数据备份
```bash
# 备份数据库
cp data/book_reader.db backup/book_reader_$(date +%Y%m%d).db

# 备份上传文件
tar -czf backup/uploads_$(date +%Y%m%d).tar.gz app/static/uploads/
```

## 🤝 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📝 更新日志

### v2.0.0 (最新)
- ✅ 重构代码架构，提高可维护性
- ✅ 添加完善的错误处理和日志记录
- ✅ 优化数据库连接和性能
- ✅ 增强安全性和认证机制
- ✅ 完整的Docker部署方案
- ✅ 添加自动化部署脚本
- ✅ 优化前端用户界面
- ✅ 改进文件上传处理

### v1.0.0
- ✅ 基础功能实现
- ✅ 用户认证系统
- ✅ 书籍管理功能
- ✅ 阅读计时功能

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 联系方式

如有问题或建议，请通过以下方式联系：
- 提交 Issue: [GitHub Issues](https://github.com/your-username/book-reader-app/issues)
- 邮箱: your-email@example.com

---

**开始你的阅读之旅吧！** 📚✨