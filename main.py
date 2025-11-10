"""
应用入口文件
"""
import os
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))

# 导入FastAPI应用实例
from app.main import app

if __name__ == "__main__":
    import uvicorn
    from dotenv import load_dotenv

    # 加载环境变量
    load_dotenv()

    # 从环境变量读取配置
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8002"))
    env = os.getenv("ENV", "development")
    reload = env == "development"

    # 运行应用
    if reload:
        # 开发环境使用字符串路径以支持热重载
        uvicorn.run(
            "app.main:app",
            host=host,
            port=port,
            reload=reload,
            log_level="info"
        )
    else:
        # 生产环境直接使用应用实例
        uvicorn.run(
            app,
            host=host,
            port=port,
            reload=reload,
            log_level="info"
        )
