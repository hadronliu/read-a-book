"""
数据库配置和会话管理
"""
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool
from contextlib import contextmanager
import os
from dotenv import load_dotenv

load_dotenv()

# 配置日志
logger = logging.getLogger(__name__)

# 数据库配置
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./book_reader.db"  # 使用更有意义的默认数据库名
)

# 根据数据库类型选择引擎参数
if DATABASE_URL.startswith("sqlite"):
    # SQLite 配置 - 优化并发性能
    engine = create_engine(
        DATABASE_URL,
        connect_args={
            "check_same_thread": False,
            "timeout": 20,  # 增加超时时间
        },
        poolclass=StaticPool,
        echo=os.getenv("ENV") == "development",  # 开发环境显示SQL
    )
    logger.info(f"SQLite 数据库已初始化: {DATABASE_URL}")
else:
    # MySQL/PostgreSQL 配置
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
        echo=os.getenv("ENV") == "development",
    )
    logger.info(f"数据库已初始化: {DATABASE_URL}")

# 创建会话工厂 - 优化会话配置
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False  # 防止对象在会话提交后过期
)

# 创建基类
Base = declarative_base()


def get_db():
    """
    获取数据库会话的依赖注入函数
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"数据库会话错误: {e}")
        db.rollback()
        raise
    finally:
        db.close()


@contextmanager
def get_db_context():
    """
    上下文管理器方式获取数据库会话
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        logger.error(f"数据库操作错误: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def init_db():
    """
    初始化数据库，创建所有表
    """
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("数据库表创建成功")
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        raise


def test_db_connection():
    """
    测试数据库连接
    """
    try:
        with engine.connect() as connection:
            from sqlalchemy import text
            result = connection.execute(text("SELECT 1"))
            logger.info("数据库连接测试成功")
            return True
    except Exception as e:
        logger.error(f"数据库连接测试失败: {e}")
        return False
