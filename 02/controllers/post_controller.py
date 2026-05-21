from typing import Literal

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from controllers.user_controller import ensure_user_exists
from models.post_like_model import PostLike
from models.post_model import Post
from models.user_model import User
from schemas.post_schema import (
    LikeToggleRequest,
    LikeToggleResponse,
    PostCreateRequest,
    PostDetailResponse,
    PostListItemResponse,
    PostListResponse,
)


def get_post_or_404(db: Session, post_id: int) -> Post:
    post = db.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
    return post


def create_post(db: Session, payload: PostCreateRequest) -> PostDetailResponse:
    user = ensure_user_exists(db, payload.user_id)

    post = Post(
        user_id=user.id,
        title=payload.title,
        content=payload.content,
    )
    db.add(post)
    db.commit()
    db.refresh(post)

    return PostDetailResponse(
        id=post.id,
        title=post.title,
        content=post.content,
        author_nickname=user.nickname,
        like_count=0,
        view_count=post.view_count,
        created_at=post.created_at,
    )


def list_posts(
    db: Session,
    page: int,
    size: int,
    keyword: str | None,
    sort: Literal["latest", "likes", "views"],
) -> PostListResponse:
    query = (
        db.query(
            Post.id,
            Post.title,
            User.nickname.label("author_nickname"),
            Post.view_count,
            Post.created_at,
            func.count(PostLike.user_id).label("like_count"),
        )
        .join(User, User.id == Post.user_id)
        .outerjoin(PostLike, PostLike.post_id == Post.id)
    )

    if keyword:
        query = query.filter(Post.title.ilike(f"%{keyword}%"))

    query = query.group_by(Post.id, Post.title, User.nickname, Post.view_count, Post.created_at)

    if sort == "latest":
        query = query.order_by(Post.id.desc())
    elif sort == "likes":
        query = query.order_by(func.count(PostLike.user_id).desc(), Post.id.desc())
    elif sort == "views":
        query = query.order_by(Post.view_count.desc(), Post.id.desc())

    total = query.count()
    rows = query.offset((page - 1) * size).limit(size).all()

    items = [
        PostListItemResponse(
            id=row.id,
            title=row.title,
            author_nickname=row.author_nickname,
            like_count=row.like_count,
            view_count=row.view_count,
            created_at=row.created_at,
        )
        for row in rows
    ]

    return PostListResponse(
        items=items,
        page=page,
        size=size,
        total=total,
        has_next=(page * size) < total,
    )


def get_post_detail(db: Session, post_id: int) -> PostDetailResponse:
    post = get_post_or_404(db, post_id)
    post.view_count += 1
    db.commit()
    db.refresh(post)

    author = db.get(User, post.user_id)
    like_count = db.query(PostLike).filter(PostLike.post_id == post.id).count()

    return PostDetailResponse(
        id=post.id,
        title=post.title,
        content=post.content,
        author_nickname=author.nickname if author else "",
        like_count=like_count,
        view_count=post.view_count,
        created_at=post.created_at,
    )


def toggle_like(db: Session, post_id: int, payload: LikeToggleRequest) -> LikeToggleResponse:
    get_post_or_404(db, post_id)
    ensure_user_exists(db, payload.user_id)

    existing = (
        db.query(PostLike)
        .filter(PostLike.post_id == post_id, PostLike.user_id == payload.user_id)
        .first()
    )

    if existing:
        db.delete(existing)
        liked = False
    else:
        db.add(PostLike(post_id=post_id, user_id=payload.user_id))
        liked = True

    db.commit()

    like_count = db.query(PostLike).filter(PostLike.post_id == post_id).count()

    return LikeToggleResponse(
        post_id=post_id,
        liked=liked,
        like_count=like_count,
    )
