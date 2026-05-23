from fastapi import HTTPException
from sqlalchemy.orm import Session

from controllers.post_controller import get_post_or_404
from controllers.user_controller import ensure_user_exists
from models.comment_model import Comment
from models.user_model import User
from schemas.comment_schema import (
    CommentCreateRequest,
    CommentListResponse,
    CommentResponse,
)


def create_comment(db: Session, post_id: int, payload: CommentCreateRequest) -> CommentResponse:
    get_post_or_404(db, post_id)
    user = ensure_user_exists(db, payload.user_id)

    comment = Comment(
        post_id=post_id,
        user_id=user.id,
        content=payload.content,
    )

    db.add(comment)
    db.commit()
    db.refresh(comment)

    return CommentResponse(
        id=comment.id,
        post_id=comment.post_id,
        user_id=comment.user_id,
        author_nickname=user.nickname,
        content=comment.content,
        created_at=comment.created_at,
    )


def list_comments(db: Session, post_id: int) -> CommentListResponse:
    get_post_or_404(db, post_id)

    rows = (
        db.query(Comment, User.nickname)
        .join(User, User.id == Comment.user_id)
        .filter(Comment.post_id == post_id)
        .order_by(Comment.id.asc())
        .all()
    )

    items = [
        CommentResponse(
            id=comment.id,
            post_id=comment.post_id,
            user_id=comment.user_id,
            author_nickname=nickname,
            content=comment.content,
            created_at=comment.created_at,
        )
        for comment, nickname in rows
    ]

    return CommentListResponse(
        items=items,
        total=len(items),
    )
