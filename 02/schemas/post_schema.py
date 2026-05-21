from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class PostCreateRequest(BaseModel):
    user_id: int
    title: str = Field(..., min_length=1, max_length=100)
    content: str = Field(..., min_length=1, max_length=5000)


class PostListItemResponse(BaseModel):
    id: int
    title: str
    author_nickname: str
    like_count: int
    view_count: int
    created_at: datetime


class PostDetailResponse(BaseModel):
    id: int
    title: str
    content: str
    author_nickname: str
    like_count: int
    view_count: int
    created_at: datetime


class PostListResponse(BaseModel):
    items: list[PostListItemResponse]
    page: int
    size: int
    total: int
    has_next: bool


class LikeToggleRequest(BaseModel):
    user_id: int


class LikeToggleResponse(BaseModel):
    post_id: int
    liked: bool
    like_count: int
