"""
API 路由定义
"""
import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.book import User
from app.schemas.book import (
    BookCreate, BookUpdate, BookResponse,
    ReadingSessionCreate, ReadingSessionUpdate, ReadingSessionResponse,
    UserCreate, UserResponse, UserLogin, Token, RandomBookResponse
)
from app.services.auth import (
    get_current_user, authenticate_user, create_access_token,
    hash_password, is_valid_password
)
from app.services.book_service import BookService, ReadingSessionService
import os
import aiofiles
from pathlib import Path

# 配置日志
logger = logging.getLogger(__name__)

# 创建路由器
router = APIRouter()

# 文件上传配置
UPLOAD_DIR = Path("app/static/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# 文件上传限制
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", "10485760"))  # 10MB
ALLOWED_EXTENSIONS = os.getenv("ALLOWED_EXTENSIONS", "jpg,jpeg,png,gif,webp").split(",")


def validate_file(file: UploadFile) -> bool:
    """验证上传文件"""
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file provided"
        )

    # 检查文件大小
    if hasattr(file, 'size') and file.size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size exceeds maximum allowed size of {MAX_FILE_SIZE} bytes"
        )

    # 检查文件扩展名
    file_extension = Path(file.filename).suffix.lower().lstrip('.')
    if file_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    return True


# ==================== 用户相关 API ====================

@router.post("/auth/register", response_model=UserResponse, tags=["Auth"])
def register(user: UserCreate, db: Session = Depends(get_db)):
    """
    用户注册
    """
    try:
        logger.info(f"用户注册请求: {user.username}")

        # 验证密码强度
        if not is_valid_password(user.password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 6 characters and contain both letters and numbers"
            )

        # 检查用户名长度
        if len(user.username.strip()) < 3:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username must be at least 3 characters"
            )

        # 检查用户是否已存在
        existing_user = db.query(User).filter(User.username == user.username.strip()).first()
        if existing_user:
            logger.warning(f"用户名已存在: {user.username}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )

        # 检查邮箱是否已存在（如果提供）
        if user.email:
            existing_email = db.query(User).filter(User.email == user.email).first()
            if existing_email:
                logger.warning(f"邮箱已存在: {user.email}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )

        # 创建新用户
        db_user = User(
            username=user.username.strip(),
            email=user.email.strip() if user.email else None,
            hashed_password=hash_password(user.password)
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        logger.info(f"用户注册成功: {user.username} (ID: {db_user.id})")
        return db_user

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"用户注册失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed due to internal error"
        )


@router.post("/auth/login", response_model=Token, tags=["Auth"])
def login(user: UserLogin, db: Session = Depends(get_db)):
    """
    用户登录
    """
    db_user = authenticate_user(db, user.username, user.password)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    access_token = create_access_token(data={"sub": db_user.id})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/auth/me", response_model=UserResponse, tags=["Auth"])
def get_me(current_user: User = Depends(get_current_user)):
    """
    获取当前用户信息
    """
    return current_user


# ==================== 书籍相关 API ====================

@router.post("/books", response_model=BookResponse, tags=["Books"])
def create_book(
    book: BookCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    创建书籍
    """
    return BookService.create_book(db, book, current_user.id)


@router.get("/books", response_model=list[BookResponse], tags=["Books"])
def list_books(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取用户的所有书籍
    """
    return BookService.get_user_books(db, current_user.id, skip, limit)


@router.get("/books/random", response_model=RandomBookResponse, tags=["Books"])
def get_random_book(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    随机获取一本书籍
    """
    book = BookService.get_random_book(db, current_user.id)
    return RandomBookResponse(
        id=book.id,
        title=book.title,
        cover_url=book.cover_url,
        description=book.description
    )


@router.get("/books/{book_id}", response_model=BookResponse, tags=["Books"])
def get_book(
    book_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取书籍详情
    """
    return BookService.get_book(db, book_id, current_user.id)


@router.put("/books/{book_id}", response_model=BookResponse, tags=["Books"])
def update_book(
    book_id: int,
    book_update: BookUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新书籍
    """
    return BookService.update_book(db, book_id, current_user.id, book_update)


@router.delete("/books/{book_id}", tags=["Books"])
def delete_book(
    book_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    删除书籍
    """
    BookService.delete_book(db, book_id, current_user.id)
    return {"message": "Book deleted successfully"}


@router.post("/books/{book_id}/upload-cover", response_model=BookResponse, tags=["Books"])
async def upload_cover(
    book_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    上传书籍封面
    """
    # 验证书籍存在
    book = BookService.get_book(db, book_id, current_user.id)
    
    # 验证文件类型
    allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only images are allowed."
        )
    
    # 保存文件
    file_extension = Path(file.filename).suffix
    file_name = f"book_{book_id}_{current_user.id}{file_extension}"
    file_path = UPLOAD_DIR / file_name
    
    contents = await file.read()
    with open(file_path, "wb") as f:
        f.write(contents)
    
    # 更新书籍封面 URL
    cover_url = f"/static/uploads/{file_name}"
    book_update = BookUpdate(cover_url=cover_url)
    return BookService.update_book(db, book_id, current_user.id, book_update)


# ==================== 阅读记录相关 API ====================

@router.post("/reading-sessions", response_model=ReadingSessionResponse, tags=["Reading Sessions"])
def create_reading_session(
    session: ReadingSessionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    创建阅读记录
    """
    return ReadingSessionService.create_session(db, session, current_user.id)


@router.get("/reading-sessions", response_model=list[ReadingSessionResponse], tags=["Reading Sessions"])
def list_reading_sessions(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取用户的所有阅读记录
    """
    return ReadingSessionService.get_user_sessions(db, current_user.id, skip, limit)


@router.get("/reading-sessions/{session_id}", response_model=ReadingSessionResponse, tags=["Reading Sessions"])
def get_reading_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取阅读记录详情
    """
    return ReadingSessionService.get_session(db, session_id, current_user.id)


@router.put("/reading-sessions/{session_id}", response_model=ReadingSessionResponse, tags=["Reading Sessions"])
def update_reading_session(
    session_id: int,
    session_update: ReadingSessionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新阅读记录
    """
    return ReadingSessionService.update_session(db, session_id, current_user.id, session_update)


@router.get("/books/{book_id}/reading-sessions", response_model=list[ReadingSessionResponse], tags=["Reading Sessions"])
def get_book_reading_sessions(
    book_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取书籍的所有阅读记录
    """
    # 验证书籍存在
    BookService.get_book(db, book_id, current_user.id)
    return ReadingSessionService.get_book_sessions(db, book_id, current_user.id)


# ==================== 统计相关 API ====================

@router.get("/stats/total-reading-time", tags=["Statistics"])
def get_total_reading_time(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取用户的总阅读时长
    """
    total_minutes = ReadingSessionService.get_total_reading_time(db, current_user.id)
    return {
        "total_minutes": total_minutes,
        "total_hours": round(total_minutes / 60, 2),
        "book_count": BookService.get_book_count(db, current_user.id)
    }


@router.get("/stats/book/{book_id}/reading-time", tags=["Statistics"])
def get_book_reading_time(
    book_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取书籍的总阅读时长
    """
    # 验证书籍存在
    book = BookService.get_book(db, book_id, current_user.id)
    total_minutes = ReadingSessionService.get_book_total_reading_time(db, book_id, current_user.id)
    return {
        "book_id": book_id,
        "book_title": book.title,
        "total_minutes": total_minutes,
        "total_hours": round(total_minutes / 60, 2)
    }
