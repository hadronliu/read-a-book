"""
书籍和阅读记录数据库模型
"""
from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class User(Base):
    """用户模型"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=True)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    books = relationship("Book", back_populates="owner", cascade="all, delete-orphan")
    reading_sessions = relationship("ReadingSession", back_populates="user", cascade="all, delete-orphan")


class Book(Base):
    """书籍模型"""
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    cover_url = Column(Text, nullable=True)  # 书籍封面 URL
    description = Column(Text, nullable=True)  # 书籍描述
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    owner = relationship("User", back_populates="books")
    reading_sessions = relationship("ReadingSession", back_populates="book", cascade="all, delete-orphan")


class ReadingSession(Base):
    """阅读记录模型"""
    __tablename__ = "reading_sessions"

    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # 时间记录
    started_at = Column(DateTime, default=datetime.utcnow)  # 开始时间
    paused_at = Column(DateTime, nullable=True)  # 暂停时间
    resumed_at = Column(DateTime, nullable=True)  # 恢复时间
    
    # 时长统计（单位：分钟）
    total_minutes = Column(Float, default=0)  # 总阅读时长
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    book = relationship("Book", back_populates="reading_sessions")
    user = relationship("User", back_populates="reading_sessions")
