from datetime import datetime, timezone
from typing import Dict, Set, Literal

from fastapi import FastAPI, HTTPException, Query, status
from pydantic import BaseModel, Field

app = FastAPI(
    title="Simple Community API",
    version="0.2.0",
    summary="인증 없는 데모용 커뮤니티 서버",
    description="""
기능:
- 닉네임 설정
- 글 작성
- 글 목록 조회
- 글 상세 조회(조회수 증가)
- 좋아요 토글
- 검색 / 페이지네이션 / 정렬
""",
)

users: Dict[int, dict] = {}
posts: Dict[int, dict] = {}
next_post_id = 1


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def ensure_user_exists(user_id: int) -> dict:
    if user_id not in users:
        users[user_id] = {
            "user_id": user_id,
            "nickname": f"guest{user_id}",
        }
    return users[user_id]


def get_post_or_404(post_id: int) -> dict:
    post = posts.get(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
    return post


class NicknameUpdateRequest(BaseModel):
    nickname: str = Field(..., min_length=2, max_length=20)


class UserResponse(BaseModel):
    user_id: int
    nickname: str


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


def build_post_list_item(post: dict) -> PostListItemResponse:
    return PostListItemResponse(
        id=post["id"],
        title=post["title"],
        author_nickname=post["author_nickname"],
        like_count=len(post["liked_user_ids"]),
        view_count=post["view_count"],
        created_at=post["created_at"],
    )


def build_post_detail(post: dict) -> PostDetailResponse:
    return PostDetailResponse(
        id=post["id"],
        title=post["title"],
        content=post["content"],
        author_nickname=post["author_nickname"],
        like_count=len(post["liked_user_ids"]),
        view_count=post["view_count"],
        created_at=post["created_at"],
    )


@app.get("/", summary="헬스 체크")
async def root():
    return {"message": "Community server is running"}


@app.put(
    "/users/{user_id}/nickname",
    response_model=UserResponse,
    summary="닉네임 설정",
)
async def set_nickname(user_id: int, payload: NicknameUpdateRequest):
    nickname = payload.nickname.strip()

    if not nickname:
        raise HTTPException(status_code=400, detail="닉네임은 공백일 수 없습니다.")

    for existing_user_id, user in users.items():
        if existing_user_id != user_id and user["nickname"] == nickname:
            raise HTTPException(status_code=409, detail="이미 사용 중인 닉네임입니다.")

    users[user_id] = {
        "user_id": user_id,
        "nickname": nickname,
    }
    return users[user_id]


@app.post(
    "/posts",
    response_model=PostDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="글 작성",
)
async def create_post(payload: PostCreateRequest):
    global next_post_id

    user = ensure_user_exists(payload.user_id)

    post = {
        "id": next_post_id,
        "user_id": payload.user_id,
        "author_nickname": user["nickname"],
        "title": payload.title,
        "content": payload.content,
        "view_count": 0,
        "liked_user_ids": set(),  # type: Set[int]
        "created_at": now_utc(),
    }

    posts[next_post_id] = post
    next_post_id += 1

    return build_post_detail(post)


@app.get(
    "/posts",
    response_model=PostListResponse,
    summary="글 목록 조회",
)
async def list_posts(
    page: int = Query(1, ge=1, description="페이지 번호"),
    size: int = Query(10, ge=1, le=100, description="페이지 크기"),
    keyword: str | None = Query(None, description="제목 검색어"),
    sort: Literal["latest", "likes", "views"] = Query("latest", description="정렬 기준"),
):
    filtered_posts = list(posts.values())

    if keyword:
        keyword_lower = keyword.lower()
        filtered_posts = [
            post for post in filtered_posts
            if keyword_lower in post["title"].lower()
        ]

    if sort == "latest":
        filtered_posts.sort(key=lambda x: x["id"], reverse=True)
    elif sort == "likes":
        filtered_posts.sort(key=lambda x: len(x["liked_user_ids"]), reverse=True)
    elif sort == "views":
        filtered_posts.sort(key=lambda x: x["view_count"], reverse=True)

    total = len(filtered_posts)
    start = (page - 1) * size
    end = start + size
    paged_posts = filtered_posts[start:end]

    return PostListResponse(
        items=[build_post_list_item(post) for post in paged_posts],
        page=page,
        size=size,
        total=total,
        has_next=end < total,
    )


@app.get(
    "/posts/{post_id}",
    response_model=PostDetailResponse,
    summary="글 상세 조회",
)
async def get_post_detail(post_id: int):
    post = get_post_or_404(post_id)
    post["view_count"] += 1
    return build_post_detail(post)


@app.post(
    "/posts/{post_id}/like",
    response_model=LikeToggleResponse,
    summary="좋아요 토글",
)
async def toggle_like(post_id: int, payload: LikeToggleRequest):
    post = get_post_or_404(post_id)
    ensure_user_exists(payload.user_id)

    liked_user_ids: Set[int] = post["liked_user_ids"]

    if payload.user_id in liked_user_ids:
        liked_user_ids.remove(payload.user_id)
        liked = False
    else:
        liked_user_ids.add(payload.user_id)
        liked = True

    return LikeToggleResponse(
        post_id=post_id,
        liked=liked,
        like_count=len(liked_user_ids),
    )
