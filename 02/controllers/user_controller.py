from fastapi import HTTPException
from sqlalchemy.orm import Session

from models.user_model import User


def ensure_user_exists(db: Session, user_id: int) -> User:
    user = db.get(User, user_id)
    if user:
        return user

    user = User(id=user_id, nickname=f"guest{user_id}")
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def set_nickname(db: Session, user_id: int, nickname: str) -> User:
    nickname = nickname.strip()
    if not nickname:
        raise HTTPException(status_code=400, detail="닉네임은 공백일 수 없습니다.")

    existing = db.query(User).filter(User.nickname == nickname, User.id != user_id).first()
    if existing:
        raise HTTPException(status_code=409, detail="이미 사용 중인 닉네임입니다.")

    user = db.get(User, user_id)
    if user is None:
        user = User(id=user_id, nickname=nickname)
        db.add(user)
    else:
        user.nickname = nickname

    db.commit()
    db.refresh(user)
    return user
