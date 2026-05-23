from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from controllers.ai_controller import (
    summarize_comments as summarize_comments_service,
    summarize_post as summarize_post_service,
)
from database import get_db
from schemas.ai_schema import SummaryResponse

router = APIRouter(prefix="/ai", tags=["AI"])


@router.post(
    "/posts/{post_id}/summary",
    response_model=SummaryResponse,
    summary="게시글 AI 요약",
)
def summarize_post(post_id: int, db: Session = Depends(get_db)):
    return summarize_post_service(db, post_id)


@router.post(
    "/posts/{post_id}/comments/summary",
    response_model=SummaryResponse,
    summary="댓글 AI 요약",
)
def summarize_comments(post_id: int, db: Session = Depends(get_db)):
    return summarize_comments_service(db, post_id)
