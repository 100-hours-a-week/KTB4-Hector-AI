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
# 회고
## 5/19
강의시간에 배웠던 것을 바탕으로 FastAPI를 이용하여 커뮤니티 서버를 만들어 보았다. 닉네임, 글 작성, 댓글, 좋아요 기능을 넣었으며 DB는 아직 실습을 안했기 때문에 연결하지 않았다. 
pydantic을 이용하여 유효성을 검증하였고 일단 하나의 main코드에 모든 기능을 넣어 놨다. Swagger와 클라이언트 코드를 이용하여 실험했을 때 잘 동작했다. 다만 아직 저장소가 휘발성이여서
다시 실행하면 저장되었던 모든 정보가 초기화되었다.
## 5/21
오늘 강의 시간에 라우터, 컨트롤러, 모델에 대해 배웠다. 이를 이용하여 내 서버의 구조를 바꿔보았다. 또 Dbeaver와 MySql을 이용하여 DB테이블을 만들고 서버와 연결했다. SQLD와 정보처리기사를 준비했을 때
배운 SQL문이 생각이 나서 DB를 구축하는데는 비교적 수월했다. 하지만 이 DB를 내 서버와 연결 시키는 것은 AI의 도움을 받았다. 라우터를 통해 요청을 받고 pydantic을 통해 요청을 검사하고 그 값을 컨트롤러에 전달하면
모델이 DB에 접근하는 과정을 이해했다. 덕분에 main.py에 200줄이 넘어가는 코드를 각 디렉토리에 분해하였다.
## 5/22
오늘은 전에 배웠던 Ollama를 이용하여 LM으로 글, 댓글 요약하는 기능을 추가해보았다. Ollama의 gemma2를 이용했으며 내가 잘 이해한지 모르겠지만 솔직하게 말하면 일단 ollama를 http://localhost:11434/api에
서브했다. 컨트롤러에 프롬프트를 부착하여 해당 URL로 보내면 Ollama가 값을 출력하여 클라이언트에게 전달하는 구조라고 이해하였다.
## 5/23
마지막으로 점검하는 시간을 가졌다. Swagger와 DBeaver를 이용하여 검사하였으며 각 기능을 테스트해보았다.
## 최종
예전에 챗봇을 만들었던 기억이 있다. LLama3 모델을 파인튜닝하여 운동 전문 챗봇으로 만들었었다. 당시 "전에 했던 대화들과 유저 정보를 LM이 조회해서 정보를 출력했으면 좋을 텐데"라는 고민이 있었지만 DB 연결을
직접 해본적도 없었고 FastAPI는 사용해봤지만 숙달이 안되어 힘들었던 기억이 있다. 이번 과제에 API서버 서빙과 DB연결을 하면서 많은 것을 느꼈다. 물론 AI의 도움이 있었지만 각 기능이 연결되어 동작하는 것을 봤을 때
기뻤다. 또 전에는 모든 코드를 하나의 파일에 몰아 넣었었다. 다른 사람들의 깃허브 코드들을 보면서 왜 파일을 저렇게 나눠놓을까?라는 의문을 가졌었다. 당시에는 파일을 나누면 헷갈리고 실행할 때 모두 연결시켜야 하고
파일 하나만 실행시키면 편한데 왜 그럴까?라는 생각이 지배적이였다. 하지만 이번 과제를 하면서 생각이 많이 바꼈다. 처음에 라우터, 컨트롤러, 모델을 나눴을 때 각 기능과 동작 과정을 이해하는 것이 어려웠다. 이해를 하고 나서도
장점을 크게 채감하지 못했다. 하지만 회고에서 나왔다시피 처음에 큰 틀을 잡고 하나씩 기능을 추가했다. DB, LM API연결을 할 때 router, controller 마지막으로 main코드에 몇 줄 적으면 끝이였다. 원래 였으면 main코드를 뜯어서 틀린
부분을 찾고 수정하고 디버깅해야했지만 이번에는 디버깅이 나도 해당 파일에 들어가서 그 부분을 찾고 수정하는게 수월했다. 이번 과제를 통해 정말 많이 배웠다.
