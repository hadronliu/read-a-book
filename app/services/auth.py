"""
认证和授权服务
"""
import logging
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.models.book import User
from app.database import get_db
import os
from dotenv import load_dotenv

load_dotenv()

# 配置日志
logger = logging.getLogger(__name__)

# 密码加密配置
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT 配置
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
if SECRET_KEY == "your-secret-key-change-this-in-production":
    logger.warning("使用默认密钥，生产环境中请更改 SECRET_KEY")

ALGORITHM = os.getenv("ALGORITHM", "HS256")
try:
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))  # 默认24小时
except ValueError:
    logger.warning("ACCESS_TOKEN_EXPIRE_MINUTES 配置错误，使用默认值")
    ACCESS_TOKEN_EXPIRE_MINUTES = 1440

# HTTP Bearer 认证
security = HTTPBearer()


def hash_password(password: str) -> str:
    """
    对密码进行哈希处理

    Args:
        password: 原始密码

    Returns:
        哈希后的密码
    """
    if not password:
        raise ValueError("密码不能为空")

    try:
        # bcrypt限制密码最大72字节，超出部分需要截断
        if len(password.encode('utf-8')) > 72:
            password = password.encode('utf-8')[:72].decode('utf-8', errors='ignore')
            logger.warning("密码过长已截断到72字节")

        hashed = pwd_context.hash(password)
        logger.debug("密码哈希成功")
        return hashed
    except Exception as e:
        logger.error(f"密码哈希失败: {e}")
        raise


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证密码

    Args:
        plain_password: 原始密码
        hashed_password: 哈希密码

    Returns:
        验证结果
    """
    if not plain_password or not hashed_password:
        return False

    try:
        # bcrypt限制密码最大72字节，超出部分需要截断
        if len(plain_password.encode('utf-8')) > 72:
            plain_password = plain_password.encode('utf-8')[:72].decode('utf-8', errors='ignore')

        result = pwd_context.verify(plain_password, hashed_password)
        logger.debug(f"密码验证结果: {result}")
        return result
    except Exception as e:
        logger.error(f"密码验证失败: {e}")
        return False


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    创建 JWT token

    Args:
        data: 要编码的数据
        expires_delta: 过期时间增量

    Returns:
        JWT token
    """
    try:
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

        # 确保用户ID是字符串（JWT标准要求）
        if "sub" in to_encode:
            to_encode["sub"] = str(to_encode["sub"])
            to_encode["iat"] = datetime.utcnow()  # 添加签发时间

        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        logger.debug("JWT token 创建成功")
        return encoded_jwt
    except Exception as e:
        logger.error(f"JWT token 创建失败: {e}")
        raise


def verify_token(token: str) -> dict:
    """
    验证 JWT token

    Args:
        token: JWT token

    Returns:
        解码后的 payload

    Raises:
        HTTPException: token 无效时
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        token_type = payload.get("type", "access")

        if user_id is None:
            logger.warning("Token 中缺少用户ID")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials: missing user_id",
            )

        if token_type != "access":
            logger.warning(f"无效的 token 类型: {token_type}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
            )

        # 确保user_id是整数
        try:
            user_id = int(user_id)
        except (ValueError, TypeError):
            logger.warning(f"无效的用户ID格式: {user_id}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user_id format",
            )

        logger.debug(f"Token 验证成功，用户ID: {user_id}")
        return {"user_id": user_id}
    except JWTError as e:
        logger.warning(f"JWT token 验证失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    获取当前登录用户

    Args:
        credentials: 认证凭据
        db: 数据库会话

    Returns:
        当前用户对象

    Raises:
        HTTPException: 用户不存在或认证失败时
    """
    try:
        token = credentials.credentials
        payload = verify_token(token)
        user_id = payload.get("user_id")

        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            logger.warning(f"用户不存在: {user_id}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )

        logger.debug(f"用户认证成功: {user.username}")
        return user
    except Exception as e:
        logger.error(f"获取当前用户失败: {e}")
        raise


def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """
    认证用户

    Args:
        db: 数据库会话
        username: 用户名
        password: 密码

    Returns:
        认证成功的用户对象，失败返回 None
    """
    try:
        if not username or not password:
            logger.warning("用户名或密码为空")
            return None

        user = db.query(User).filter(User.username == username).first()
        if not user:
            logger.warning(f"用户不存在: {username}")
            return None

        if not verify_password(password, user.hashed_password):
            logger.warning(f"密码错误: {username}")
            return None

        logger.info(f"用户认证成功: {username}")
        return user
    except Exception as e:
        logger.error(f"用户认证失败: {e}")
        return None


def is_valid_password(password: str) -> bool:
    """
    验证密码强度

    Args:
        password: 密码

    Returns:
        密码是否符合要求
    """
    if not password:
        return False

    # 至少6位，包含字母和数字
    if len(password) < 6:
        return False

    has_letter = any(c.isalpha() for c in password)
    has_digit = any(c.isdigit() for c in password)

    return has_letter and has_digit