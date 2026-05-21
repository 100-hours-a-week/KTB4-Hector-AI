from typing import Literal

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from controllers.post_controller import (
    create_post as create_post_service,
    get_post_detail as get_post_detail_service,
    list_posts as list_posts_service,
    toggle_like as toggle_like_service,
)
from database import get_db
from schemas.post_schema import (
    LikeToggleRequest,
    LikeToggleResponse,
    PostCreateRequest,
    PostDetailResponse,
    PostListResponse,
)

router = APIRouter(prefix="/posts", tags=["Posts"])


@router.post("", response_model=PostDetailResponse, status_code=status.HTTP_201_CREATED, summary="글 작성")
def create_post(payload: PostCreateRequest, db: Session = Depends(get_db)):
    return create_post_service(db, payload)


@router.get("", response_model=PostListResponse, summary="글 목록 조회")
def list_posts(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    keyword: str | None = Query(None),
    sort: Literal["latest", "likes", "views"] = Query("latest"),
    db: Session = Depends(get_db),
):
    return list_posts_service(db, page, size, keyword, sort)


@router.get("/{post_id}", response_model=PostDetailResponse, summary="글 상세 조회")
def get_post_detail(post_id: int, db: Session = Depends(get_db)):
    return get_post_detail_service(db, post_id)


@router.post("/{post_id}/like", response_model=LikeToggleResponse, summary="좋아요 토글")
def toggle_like(post_id: int, payload: LikeToggleRequest, db: Session = Depends(get_db)):
    return toggle_like_service(db, post_id, payload)
