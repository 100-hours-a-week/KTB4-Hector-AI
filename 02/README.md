# 커뮤니티 서비스

## 구조
```
project/
├── main.py
├── database.py
├── routers/
│   ├── user_router.py
│   ├── post_router.py
│   ├── comment_router.py
│   └── ai_router.py
├── controllers/
│   ├── user_controller.py
│   ├── post_controller.py
│   ├── comment_controller.py
│   └── ai_controller.py
├── models/
│   ├── user_model.py
│   ├── post_model.py
│   ├── post_like_model.py
│   └── comment_model.py
└── schemas/
    ├── user_schema.py
    ├── post_schema.py
    ├── comment_schema.py
    └── ai_schema.py
```

## 주요 기능

* 사용자 닉네임 설정
* 게시글 작성
* 게시글 목록 조회
* 게시글 상세 조회
* 게시글 좋아요 토글
* DB 연결 확인

## BaseURl
* http://127.0.0.1:8000

## Swagger
* http://127.0.0.1:8000/docs

## 공 응답
* 200 OK
* 201 Created

## 실패 응답 예시
* 400 Bad Request : 잘못된 요청
* 404 Not Found : 대상 데이터 없음
* 409 Conflict : 중복 닉네임 등 충돌
* 422 Unprocessable Entity : 요청 body 검증 실패
* 500 Internal Server Error : 서버 내부 오류

## 서버 실행 코드
```
uv run uvicorn main:app --reload
```

## 커뮤니티 이용 방법

### 닉네임 설정
* swagger의 /users/{user_id}/nickname로 가서 설정하고자하는 user_id를 입력하고 원하는 닉네임을 설정
* 요청 스키마
```
{
  "nickname": "string"
}
```
* 응답 스키마
```
{
  "id": 0,
  "nickname": "string"
}
```
### 글 작성
* Swagger의 /posts으로 가서 정보를 입력
* 만약 닉네임 설정을 안하고 글을 작성하면 guest_번호로 나옴
* 요청 스키마
```
{
  "user_id": 0,
  "title": "string",
  "content": "string"
}
```
* 응답 스키마
```
{
  "id": 0,
  "title": "string",
  "content": "string",
  "author_nickname": "string",
  "like_count": 0,
  "view_count": 0,
  "created_at": "2026-05-23T04:19:11.493Z"
}
```
### 댓글 작성
* Swagger의 /posts/{post_id}/comments으로 가서 정보를 입력
* 요청 스키마
```
{
  "user_id": 0,
  "content": "string"
}
```

응답 스키마
```
{
  "id": 0,
  "post_id": 0,
  "user_id": 0,
  "author_nickname": "string",
  "content": "string",
  "created_at": "2026-05-23T04:21:14.141Z"
}
```
### 글 목록 조회
* Swagger의 /posts에 가서 page, size(몇 개), keyword(찾고자하는 단어 없으면 비워두면 됨), sort(latest, likes, views)를 설정
* 응답 스키마
```
{
  "items": [
    {
      "id": 0,
      "title": "string",
      "author_nickname": "string",
      "like_count": 0,
      "view_count": 0,
      "created_at": "2026-05-23T04:43:00.039Z"
    }
  ],
  "page": 0,
  "size": 0,
  "total": 0,
  "has_next": true
}
```
### 특정 1개의 글 검색
* Swagger의 /posts에 가서 원하는 post_id를 설정
* 응답 스키마
```
{
  "id": 0,
  "title": "string",
  "content": "string",
  "author_nickname": "string",
  "like_count": 0,
  "view_count": 0,
  "created_at": "2026-05-23T04:43:54.766Z"
}
```

### 좋아요 기능
* Swagger의 /posts/{post_id}/like에 가서 좋아요 할 post_id설정
* 입력 스키마
```
{
  "user_id": 0
}
```
* 응답 스키마
```
{
  "post_id": 0,
  "liked": true,
  "like_count": 0
}
```
* 만약 같은 사람이 같은 글에 좋아요를 한번 더 누르면 좋아요 취소
### AI 글 요약
* Swaggwer의 /ai/posts/{post_id}/summary로 가서 원하는 post_id를 입력
* 응답 스키마
```
{
  "target_type": "string",
  "target_id": 0,
  "model": "string",
  "summary": "string"
}
```

### 댓글 요약
* Swagger의 /ai/posts/{post_id}/comments/summary로 가서 원하는 post_id를 입력
* 응답 스키마
```
{
  "target_type": "string",
  "target_id": 0,
  "model": "string",
  "summary": "string"
}
```
