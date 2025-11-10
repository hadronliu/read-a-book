"""
Pydantic 数据验证模型
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


class BookBase(BaseModel):
    """书籍基础模型"""
    title: str = Field(..., min_length=1, max_length=255, description="书籍名称")
    description: Optional[str] = Field(None, max_length=1000, description="书籍描述")


class BookCreate(BookBase):
    """创建书籍的请求模型"""
    cover_url: Optional[str] = Field(None, description="书籍封面 URL")


class BookUpdate(BaseModel):
    """更新书籍的请求模型"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    cover_url: Optional[str] = Field(None)


class BookResponse(BookBase):
    """书籍响应模型"""
    id: int
    cover_url: Optional[str]
    owner_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ReadingSessionBase(BaseModel):
    """阅读记录基础模型"""
    book_id: int = Field(..., description="书籍 ID")


class ReadingSessionCreate(ReadingSessionBase):
    """创建阅读记录的请求模型"""
    pass


class ReadingSessionUpdate(BaseModel):
    """更新阅读记录的请求模型"""
    total_minutes: Optional[float] = Field(None, ge=0, description="总阅读时长（分钟）")
    paused_at: Optional[datetime] = Field(None, description="暂停时间")
    resumed_at: Optional[datetime] = Field(None, description="恢复时间")


class ReadingSessionResponse(ReadingSessionBase):
    """阅读记录响应模型"""
    id: int
    user_id: int
    started_at: datetime
    paused_at: Optional[datetime]
    resumed_at: Optional[datetime]
    total_minutes: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserBase(BaseModel):
    """用户基础模型"""
    username: str = Field(..., min_length=3, max_length=100, description="用户名")
    email: Optional[str] = Field(None, description="邮箱")


class UserCreate(UserBase):
    """创建用户的请求模型"""
    password: str = Field(..., min_length=6, description="密码")


class UserResponse(UserBase):
    """用户响应模型"""
    id: int
    created_at: datetime
    updated_at: datetime
    books: List[BookResponse] = []

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    """用户登录请求模型"""
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")


class Token(BaseModel):
    """Token 响应模型"""
    access_token: str
    token_type: str = "bearer"


class RandomBookResponse(BaseModel):
    """随机书籍响应模型"""
    id: int
    title: str
    cover_url: Optional[str]
    description: Optional[str]
