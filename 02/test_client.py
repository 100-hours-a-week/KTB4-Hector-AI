import requests
import json

BASE_URL = "http://127.0.0.1:8000"


def pretty_print(title, response):
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)
    print("STATUS:", response.status_code)
    try:
        print(json.dumps(response.json(), ensure_ascii=False, indent=2))
    except Exception:
        print(response.text)


def set_nickname(user_id: int, nickname: str):
    response = requests.put(
        f"{BASE_URL}/users/{user_id}/nickname",
        json={"nickname": nickname},
    )
    pretty_print("닉네임 설정", response)


def create_post(user_id: int, title: str, content: str):
    response = requests.post(
        f"{BASE_URL}/posts",
        json={
            "user_id": user_id,
            "title": title,
            "content": content,
        },
    )
    pretty_print("글 작성", response)


def list_posts(page=1, size=10, keyword=None, sort="latest"):
    params = {
        "page": page,
        "size": size,
        "sort": sort,
    }
    if keyword:
        params["keyword"] = keyword

    response = requests.get(
        f"{BASE_URL}/posts",
        params=params,
    )
    pretty_print("글 목록 조회", response)


def get_post_detail(post_id: int):
    response = requests.get(f"{BASE_URL}/posts/{post_id}")
    pretty_print("글 상세 조회", response)


def toggle_like(post_id: int, user_id: int):
    response = requests.post(
        f"{BASE_URL}/posts/{post_id}/like",
        json={"user_id": user_id},
    )
    pretty_print("좋아요 토글", response)


if __name__ == "__main__":
    # 1. 닉네임 설정
    set_nickname(1, "alice")
    set_nickname(2, "bob")

    # 2. 글 작성
    create_post(1, "첫 글", "안녕하세요. 첫 번째 게시글입니다.")
    create_post(2, "두 번째 글", "FastAPI로 커뮤니티 서버 만드는 중입니다.")
    create_post(1, "세 번째 글", "검색과 정렬 기능 테스트입니다.")

    # 3. 좋아요
    toggle_like(1, 2)
    toggle_like(2, 1)
    toggle_like(2, 2)

    # 4. 상세 조회(조회수 증가)
    get_post_detail(1)
    get_post_detail(1)
    get_post_detail(2)

    # 5. 목록 조회 - 최신순
    list_posts(page=1, size=10, sort="latest")

    # 6. 목록 조회 - 좋아요순
    list_posts(page=1, size=10, sort="likes")

    # 7. 목록 조회 - 조회수순
    list_posts(page=1, size=10, sort="views")

    # 8. 목록 조회 - 검색
    list_posts(page=1, size=10, keyword="세", sort="latest")
