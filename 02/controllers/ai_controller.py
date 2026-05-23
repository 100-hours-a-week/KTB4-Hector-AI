import os

import httpx
from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from controllers.post_controller import get_post_or_404
from models.comment_model import Comment
from models.post_like_model import PostLike
from models.user_model import User
from schemas.ai_schema import SummaryResponse

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/api")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma2")


def call_ollama(prompt: str) -> str:
    try:
        with httpx.Client(timeout=120.0) as client:
            response = client.post(
                f"{OLLAMA_BASE_URL}/chat",
                json={
                    "model": OLLAMA_MODEL,
                    "stream": False,
                    "messages": [
                        {
                            "role": "system",
                            "content": (
                                "너는 한국어 커뮤니티 요약 도우미다. "
                                "중복 표현 없이 핵심만 간결하게 요약해라. "
                                "추측하지 말고 입력에 있는 내용만 요약해라."
                            ),
                        },
                        {
                            "role": "user",
                            "content": prompt,
                        },
                    ],
                },
            )
            response.raise_for_status()
            data = response.json()
            return data["message"]["content"].strip()

    except httpx.RequestError:
        raise HTTPException(
            status_code=503,
            detail="Ollama 서버에 연결할 수 없습니다. ollama 실행 상태를 확인해주세요.",
        )
    except KeyError:
        raise HTTPException(
            status_code=500,
            detail="Ollama 응답 형식이 예상과 다릅니다.",
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"요약 생성 중 오류가 발생했습니다: {str(e)}",
        )


def summarize_post(db: Session, post_id: int) -> SummaryResponse:
    post = get_post_or_404(db, post_id)
    author = db.get(User, post.user_id)
    like_count = db.query(func.count(PostLike.user_id)).filter(PostLike.post_id == post.id).scalar() or 0

    prompt = f"""
아래 게시글을 읽고 한국어로 요약해줘.

출력 형식:
1. 한 줄 요약
2. 핵심 포인트 3개 이내
3. 전체 톤(예: 질문형/후기형/정보공유형)

게시글 정보:
- 제목: {post.title}
- 작성자: {author.nickname if author else "unknown"}
- 좋아요 수: {like_count}
- 조회수: {post.view_count}

본문:
{post.content}
""".strip()

    summary = call_ollama(prompt)

    return SummaryResponse(
        target_type="post",
        target_id=post_id,
        model=OLLAMA_MODEL,
        summary=summary,
    )


def summarize_comments(db: Session, post_id: int) -> SummaryResponse:
    post = get_post_or_404(db, post_id)

    rows = (
        db.query(Comment, User.nickname)
        .join(User, User.id == Comment.user_id)
        .filter(Comment.post_id == post_id)
        .order_by(Comment.id.asc())
        .all()
    )

    if not rows:
        raise HTTPException(status_code=404, detail="요약할 댓글이 없습니다.")

    comment_text = "\n".join(
        [f"- {nickname}: {comment.content}" for comment, nickname in rows]
    )

    prompt = f"""
아래는 게시글 댓글 목록이야. 한국어로 요약해줘.

출력 형식:
1. 전체 분위기
2. 주요 의견 3개 이내
3. 반복되는 질문이나 키워드

원본 게시글 제목:
{post.title}

댓글 목록:
{comment_text}
""".strip()

    summary = call_ollama(prompt)

    return SummaryResponse(
        target_type="comments",
        target_id=post_id,
        model=OLLAMA_MODEL,
        summary=summary,
    )
