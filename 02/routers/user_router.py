from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from controllers.user_controller import set_nickname as set_nickname_service
from database import get_db
from schemas.user_schema import NicknameUpdateRequest, UserResponse

router = APIRouter(prefix="/users", tags=["Users"])


@router.put("/{user_id}/nickname", response_model=UserResponse, summary="닉네임 설정")
def set_nickname(user_id: int, payload: NicknameUpdateRequest, db: Session = Depends(get_db)):
    return set_nickname_service(db, user_id, payload.nickname)
