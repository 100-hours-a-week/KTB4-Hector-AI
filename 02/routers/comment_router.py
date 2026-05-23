from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from controllers.comment_controller import (
    create_comment as create_comment_service,
    list_comments as list_comments_service,
)
from database import get_db
from schemas.comment_schema import (
    CommentCreateRequest,
    CommentListResponse,
    CommentResponse,
)

router = APIRouter(prefix="/posts", tags=["Comments"])


@router.post(
    "/{post_id}/comments",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="댓글 작성",
)
def create_comment(post_id: int, payload: CommentCreateRequest, db: Session = Depends(get_db)):
    return create_comment_service(db, post_id, payload)


@router.get(
    "/{post_id}/comments",
    response_model=CommentListResponse,
    summary="댓글 목록 조회",
)
def list_comments(post_id: int, db: Session = Depends(get_db)):
    return list_comments_service(db, post_id)
