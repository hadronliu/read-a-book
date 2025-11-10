"""
FastAPI 主应用文件
"""
import logging
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from pathlib import Path
import os
from dotenv import load_dotenv

from app.database import init_db, test_db_connection
from app.api.routes import router

# 加载环境变量
load_dotenv()

# 配置日志系统
def setup_logging():
    """配置应用日志"""
    log_level = os.getenv("LOG_LEVEL", "info").upper()

    # 创建日志格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # 配置根日志器
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
        ]
    )

    # 设置第三方库的日志级别
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)

    return logging.getLogger(__name__)

# 初始化日志
logger = setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    logger.info("🚀 应用启动中...")

    try:
        # 测试数据库连接
        if test_db_connection():
            logger.info("✅ 数据库连接成功")
        else:
            logger.error("❌ 数据库连接失败")
            raise Exception("数据库连接失败")

        # 初始化数据库表
        init_db()
        logger.info("✅ 数据库初始化完成")

        # 确保必要的目录存在
        directories = ["app/static/uploads", "app/logs"]
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
            logger.debug(f"目录已确保存在: {directory}")

        logger.info("🎉 应用启动完成")

    except Exception as e:
        logger.error(f"❌ 应用启动失败: {e}")
        raise

    yield

    # 关闭时执行
    logger.info("🛑 应用关闭中...")
    logger.info("✅ 应用已安全关闭")

# 创建 FastAPI 应用
app = FastAPI(
    title="随机阅读电子书应用",
    description="一个用 FastAPI 开发的随机阅读电子书应用",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# 添加受信任主机中间件（生产环境）
if os.getenv("ENV") == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["localhost", "127.0.0.1", "*.yourdomain.com"]
    )

# 添加 CORS 中间件
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# 全局异常处理器
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理器"""
    logger.error(f"未处理的异常: {exc}", exc_info=True)

    if os.getenv("ENV") == "production":
        return JSONResponse(
            status_code=500,
            content={"detail": "内部服务器错误"}
        )
    else:
        return JSONResponse(
            status_code=500,
            content={
                "detail": f"内部服务器错误: {str(exc)}",
                "type": type(exc).__name__
            }
        )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """HTTP异常处理器"""
    logger.warning(f"HTTP异常: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

# 配置模板
templates = Jinja2Templates(directory="app/templates")

# 挂载静态文件目录
static_dir = Path("app/static")
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
    logger.info(f"✅ 静态文件目录已挂载: {static_dir}")
else:
    logger.warning(f"⚠️ 静态文件目录不存在: {static_dir}")

# 包含 API 路由
app.include_router(router, prefix="/api", tags=["API"])
logger.info("✅ API 路由已加载")


@app.get("/", tags=["Root"])
def read_root(request: Request):
    """
    根路由 - 返回前端页面
    """
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health", tags=["Health"])
def health_check():
    """
    健康检查端点
    """
    return {"status": "healthy"}


@app.get("/my-books", tags=["Pages"])
def my_books_page(request: Request):
    """
    我的书籍页面
    """
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/debug.html", tags=["Debug"])
def debug_page():
    """
    调试页面 - 帮助诊断注册问题
    """
    debug_html = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>注册调试页面</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 20px auto; padding: 20px; }
        .section { margin: 20px 0; padding: 20px; border: 1px solid #ddd; border-radius: 8px; background: #f9f9f9; }
        .debug-info { background: #e3f2fd; padding: 10px; border-radius: 4px; margin: 10px 0; }
        .error { color: red; background: #ffebee; padding: 10px; border-radius: 4px; }
        .success { color: green; background: #e8f5e9; padding: 10px; border-radius: 4px; }
        input, button { padding: 8px 12px; margin: 5px; }
        button { cursor: pointer; background: #2196f3; color: white; border: none; border-radius: 4px; }
        button:hover { background: #1976d2; }
        pre { background: #f5f5f5; padding: 10px; border-radius: 4px; overflow-x: auto; }
    </style>
</head>
<body>
    <h1>🔍 注册功能调试页面</h1>

    <div class="section">
        <h2>📊 当前状态</h2>
        <div class="debug-info">
            <p><strong>时间:</strong> <span id="currentTime"></span></p>
            <p><strong>浏览器:</strong> <span id="browserInfo"></span></p>
            <p><strong>API基础URL:</strong> /api</p>
            <p><strong>localStorage Token:</strong> <span id="tokenStatus"></span></p>
        </div>
    </div>

    <div class="section">
        <h2>🔧 手动测试注册</h2>
        <p>请输入<strong>全新的用户名</strong>（不要使用已经存在的用户名）：</p>
        <div>
            <input type="text" id="debugUsername" placeholder="例如: user12345" value="user12345">
            <input type="email" id="debugEmail" placeholder="邮箱（可选）" value="user12345@example.com">
            <input type="password" id="debugPassword" placeholder="密码" value="123456">
            <button onclick="debugRegister()">🚀 发送注册请求</button>
        </div>
        <div id="registerResult"></div>
    </div>

    <div class="section">
        <h2>🔍 网络请求调试</h2>
        <button onclick="testConnection()">🌐 测试API连接</button>
        <button onclick="clearConsole()">🧹 清除控制台</button>
        <div id="networkResult"></div>
        <h3>请求日志:</h3>
        <pre id="requestLog"></pre>
    </div>

    <div class="section">
        <h2>🏠 返回选项</h2>
        <button onclick="window.location.href='/'">📱 返回主页</button>
        <button onclick="window.location.href='/test_login.html'">🧪 访问测试页面</button>
    </div>

    <script>
        const API_BASE = '/api';
        let requestLog = [];

        // 初始化
        document.addEventListener('DOMContentLoaded', function() {
            updateDebugInfo();
            setInterval(updateDebugInfo, 1000);
        });

        function updateDebugInfo() {
            document.getElementById('currentTime').textContent = new Date().toLocaleString();
            document.getElementById('browserInfo').textContent = navigator.userAgent;

            const token = localStorage.getItem('token');
            document.getElementById('tokenStatus').textContent = token ?
                `已保存 (${token.substring(0, 20)}...)` : '未保存';
        }

        function log(message) {
            const timestamp = new Date().toLocaleTimeString();
            const logEntry = `[${timestamp}] ${message}`;
            requestLog.push(logEntry);

            const logElement = document.getElementById('requestLog');
            logElement.textContent = requestLog.slice(-10).join('\\n');
            console.log(logEntry);
        }

        async function testConnection() {
            const resultDiv = document.getElementById('networkResult');
            log('开始测试API连接...');

            try {
                const response = await fetch('/api/../health');
                const data = await response.json();
                log(`健康检查成功: ${JSON.stringify(data)}`);
                resultDiv.innerHTML = '<div class="success">✅ API连接正常</div>';
            } catch (error) {
                log(`API连接失败: ${error.message}`);
                resultDiv.innerHTML = `<div class="error">❌ API连接失败: ${error.message}</div>`;
            }
        }

        async function debugRegister() {
            const username = document.getElementById('debugUsername').value;
            const email = document.getElementById('debugEmail').value;
            const password = document.getElementById('debugPassword').value;
            const resultDiv = document.getElementById('registerResult');

            log(`准备注册用户: ${username}, ${email}`);

            if (!username || !password) {
                log('❌ 用户名或密码为空');
                resultDiv.innerHTML = '<div class="error">❌ 用户名和密码不能为空</div>';
                return;
            }

            const requestData = { username, password };
            if (email) {
                requestData.email = email;
            }

            log(`发送请求数据: ${JSON.stringify(requestData)}`);

            try {
                const response = await fetch('${API_BASE}/auth/register', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(requestData)
                });

                log(`收到响应状态: ${response.status} ${response.statusText}`);

                const responseText = await response.text();
                log(`响应内容: ${responseText}`);

                if (response.ok) {
                    const data = JSON.parse(responseText);
                    resultDiv.innerHTML = \`
                        <div class="success">
                            ✅ 注册成功！<br>
                            用户ID: \${data.id}<br>
                            用户名: \${data.username}<br>
                            <button onclick="loginAfterRegister('\${username}', '\${password}')">🔑 立即登录</button>
                        </div>
                    \`;
                    log('✅ 注册成功！');
                } else {
                    try {
                        const errorData = JSON.parse(responseText);
                        resultDiv.innerHTML = \`<div class="error">❌ 注册失败: \${errorData.detail}</div>\`;
                        log(\`❌ 注册失败: \${errorData.detail}\`);
                    } catch {
                        resultDiv.innerHTML = \`<div class="error">❌ 注册失败: 服务器错误</div>\`;
                        log('❌ 注册失败: 服务器错误');
                    }
                }
            } catch (error) {
                log(\`❌ 网络错误: \${error.message}\`);
                resultDiv.innerHTML = \`<div class="error">❌ 网络错误: \${error.message}</div>\`;
            }
        }

        async function loginAfterRegister(username, password) {
            log(\`使用刚注册的账号登录: \${username}\`);

            try {
                const response = await fetch('${API_BASE}/auth/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ username, password })
                });

                if (response.ok) {
                    const data = await response.json();
                    localStorage.setItem('token', data.access_token);
                    log('✅ 登录成功！跳转到主页...');
                    setTimeout(() => {
                        window.location.href = '/';
                    }, 2000);
                } else {
                    log('❌ 登录失败');
                }
            } catch (error) {
                log(\`❌ 登录网络错误: \${error.message}\`);
            }
        }

        function clearConsole() {
            requestLog = [];
            document.getElementById('requestLog').textContent = '';
            log('控制台已清除');
        }
    </script>
</body>
</html>"""
    return HTMLResponse(content=debug_html)


@app.get("/test_login.html", tags=["Test"])
def test_login_page():
    """
    测试登录页面
    """
    test_html = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>登录测试</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; }
        .section { margin: 30px 0; padding: 20px; border: 1px solid #ddd; border-radius: 8px; }
        input { display: block; margin: 10px 0; padding: 8px; width: 300px; }
        button { padding: 10px 20px; margin: 10px 5px; cursor: pointer; }
        .message { margin: 10px 0; padding: 10px; border-radius: 4px; }
        .success { background: #d4edda; color: #155724; }
        .error { background: #f8d7da; color: #721c24; }
    </style>
</head>
<body>
    <h1>🔧 登录功能测试页面</h1>

    <div class="section">
        <h2>📝 注册新用户</h2>
        <input type="text" id="regUsername" placeholder="用户名" value="testuser4">
        <input type="password" id="regPassword" placeholder="密码" value="123456">
        <input type="email" id="regEmail" placeholder="邮箱" value="test4@example.com">
        <button onclick="testRegister()">注册</button>
        <div id="regMessage" class="message"></div>
    </div>

    <div class="section">
        <h2>🔑 登录测试</h2>
        <p>使用已有账号登录：</p>
        <ul>
            <li>testuser2 / 123456</li>
            <li>testuser3 / 123456</li>
        </ul>
        <input type="text" id="loginUsername" placeholder="用户名" value="testuser2">
        <input type="password" id="loginPassword" placeholder="密码" value="123456">
        <button onclick="testLogin()">登录</button>
        <div id="loginMessage" class="message"></div>
    </div>

    <div class="section">
        <h2>🏠 返回主页</h2>
        <button onclick="goToMainPage()">返回主页</button>
    </div>

    <script>
        const API_BASE = '/api';

        async function testRegister() {
            const username = document.getElementById('regUsername').value;
            const email = document.getElementById('regEmail').value;
            const password = document.getElementById('regPassword').value;
            const messageDiv = document.getElementById('regMessage');

            try {
                const response = await fetch(`${API_BASE}/auth/register`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username, email, password })
                });

                const data = await response.json();
                if (response.ok) {
                    messageDiv.className = 'message success';
                    messageDiv.innerHTML = `✅ 注册成功！用户ID: ${data.id}`;
                } else {
                    messageDiv.className = 'message error';
                    messageDiv.innerHTML = `❌ 注册失败: ${data.detail}`;
                }
            } catch (error) {
                messageDiv.className = 'message error';
                messageDiv.innerHTML = `❌ 网络错误: ${error.message}`;
            }
        }

        async function testLogin() {
            const username = document.getElementById('loginUsername').value;
            const password = document.getElementById('loginPassword').value;
            const messageDiv = document.getElementById('loginMessage');

            try {
                const response = await fetch(`${API_BASE}/auth/login`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username, password })
                });

                const data = await response.json();
                if (response.ok) {
                    messageDiv.className = 'message success';
                    messageDiv.innerHTML = `✅ 登录成功！<br>Token: ${data.access_token.substring(0, 20)}...<br>用户ID已保存到 localStorage`;
                    localStorage.setItem('token', data.access_token);
                } else {
                    messageDiv.className = 'message error';
                    messageDiv.innerHTML = `❌ 登录失败: ${data.detail}`;
                }
            } catch (error) {
                messageDiv.className = 'message error';
                messageDiv.innerHTML = `❌ 网络错误: ${error.message}`;
            }
        }

        function goToMainPage() {
            window.location.href = '/';
        }
    </script>
</body>
</html>"""
    return HTMLResponse(content=test_html)


if __name__ == "__main__":
    import uvicorn
    
    # 从环境变量读取配置，默认值为开发环境配置
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    reload = os.getenv("ENV", "development") == "development"
    
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )
