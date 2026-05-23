from datetime import datetime

from pydantic import BaseModel, Field


class CommentCreateRequest(BaseModel):
    user_id: int
    content: str = Field(..., min_length=1, max_length=1000)


class CommentResponse(BaseModel):
    id: int
    post_id: int
    user_id: int
    author_nickname: str
    content: str
    created_at: datetime


class CommentListResponse(BaseModel):
    items: list[CommentResponse]
    total: int
