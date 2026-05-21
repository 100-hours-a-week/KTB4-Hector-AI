from typing import Dict

users: Dict[int, dict] = {}
posts: Dict[int, dict] = {}

_next_post_id = 1


def get_next_post_id() -> int:
    global _next_post_id
    post_id = _next_post_id
    _next_post_id += 1
    return post_id
