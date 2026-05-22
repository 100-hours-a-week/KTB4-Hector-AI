from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

#글 작성 스키마
class PostCreateRequest(BaseModel):
    user_id: int
    title: str = Field(..., min_length=1, max_length=100)
    content: str = Field(..., min_length=1, max_length=5000)

# 글 목록 스키마
class PostListItemResponse(BaseModel):
    id: int
    title: str
    author_nickname: str
    like_count: int
    view_count: int
    created_at: datetime

# 상세보기 스키마
class PostDetailResponse(BaseModel):
    id: int
    title: str
    content: str
    author_nickname: str
    like_count: int
    view_count: int
    created_at: datetime

# 글 상세 목록 스키마
class PostListResponse(BaseModel):
    items: list[PostListItemResponse]
    page: int
    size: int
    total: int
    has_next: bool

#좋아요, 토글 요청/응답 스키마
class LikeToggleRequest(BaseModel):
    user_id: int


class LikeToggleResponse(BaseModel):
    post_id: int
    liked: bool
    like_count: int
