"""
书籍相关的业务逻辑服务
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.book import Book, ReadingSession, User
from app.schemas.book import BookCreate, BookUpdate, ReadingSessionCreate, ReadingSessionUpdate
from fastapi import HTTPException, status
from datetime import datetime
import random


class BookService:
    """书籍服务"""

    @staticmethod
    def create_book(db: Session, book: BookCreate, user_id: int) -> Book:
        """创建书籍"""
        db_book = Book(
            title=book.title,
            description=book.description,
            cover_url=book.cover_url,
            owner_id=user_id
        )
        db.add(db_book)
        db.commit()
        db.refresh(db_book)
        return db_book

    @staticmethod
    def get_book(db: Session, book_id: int, user_id: int) -> Book:
        """获取书籍（验证所有权）"""
        book = db.query(Book).filter(
            Book.id == book_id,
            Book.owner_id == user_id
        ).first()
        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Book not found"
            )
        return book

    @staticmethod
    def get_user_books(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> list:
        """获取用户的所有书籍"""
        return db.query(Book).filter(
            Book.owner_id == user_id
        ).offset(skip).limit(limit).all()

    @staticmethod
    def update_book(db: Session, book_id: int, user_id: int, book_update: BookUpdate) -> Book:
        """更新书籍"""
        book = BookService.get_book(db, book_id, user_id)
        
        update_data = book_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(book, field, value)
        
        db.add(book)
        db.commit()
        db.refresh(book)
        return book

    @staticmethod
    def delete_book(db: Session, book_id: int, user_id: int) -> None:
        """删除书籍"""
        book = BookService.get_book(db, book_id, user_id)
        db.delete(book)
        db.commit()

    @staticmethod
    def get_random_book(db: Session, user_id: int) -> Book:
        """随机获取用户的一本书籍"""
        books = db.query(Book).filter(Book.owner_id == user_id).all()
        
        if not books:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No books found"
            )
        
        return random.choice(books)

    @staticmethod
    def get_book_count(db: Session, user_id: int) -> int:
        """获取用户书籍数量"""
        return db.query(func.count(Book.id)).filter(
            Book.owner_id == user_id
        ).scalar()


class ReadingSessionService:
    """阅读记录服务"""

    @staticmethod
    def create_session(db: Session, session: ReadingSessionCreate, user_id: int) -> ReadingSession:
        """创建阅读记录"""
        # 验证书籍存在且属于用户
        book = db.query(Book).filter(
            Book.id == session.book_id,
            Book.owner_id == user_id
        ).first()
        
        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Book not found"
            )
        
        db_session = ReadingSession(
            book_id=session.book_id,
            user_id=user_id,
            started_at=datetime.utcnow()
        )
        db.add(db_session)
        db.commit()
        db.refresh(db_session)
        return db_session

    @staticmethod
    def get_session(db: Session, session_id: int, user_id: int) -> ReadingSession:
        """获取阅读记录"""
        session = db.query(ReadingSession).filter(
            ReadingSession.id == session_id,
            ReadingSession.user_id == user_id
        ).first()
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reading session not found"
            )
        return session

    @staticmethod
    def update_session(db: Session, session_id: int, user_id: int, 
                      session_update: ReadingSessionUpdate) -> ReadingSession:
        """更新阅读记录"""
        session = ReadingSessionService.get_session(db, session_id, user_id)
        
        update_data = session_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(session, field, value)
        
        db.add(session)
        db.commit()
        db.refresh(session)
        return session

    @staticmethod
    def get_book_sessions(db: Session, book_id: int, user_id: int) -> list:
        """获取书籍的所有阅读记录"""
        return db.query(ReadingSession).filter(
            ReadingSession.book_id == book_id,
            ReadingSession.user_id == user_id
        ).all()

    @staticmethod
    def get_user_sessions(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> list:
        """获取用户的所有阅读记录"""
        return db.query(ReadingSession).filter(
            ReadingSession.user_id == user_id
        ).offset(skip).limit(limit).all()

    @staticmethod
    def get_total_reading_time(db: Session, user_id: int) -> float:
        """获取用户的总阅读时长（分钟）"""
        result = db.query(func.sum(ReadingSession.total_minutes)).filter(
            ReadingSession.user_id == user_id
        ).scalar()
        return result or 0.0

    @staticmethod
    def get_book_total_reading_time(db: Session, book_id: int, user_id: int) -> float:
        """获取书籍的总阅读时长（分钟）"""
        result = db.query(func.sum(ReadingSession.total_minutes)).filter(
            ReadingSession.book_id == book_id,
            ReadingSession.user_id == user_id
        ).scalar()
        return result or 0.0
