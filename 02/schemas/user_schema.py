from pydantic import BaseModel, Field, ConfigDict

#닉네임 변경 요청 body검증
class NicknameUpdateRequest(BaseModel):
    nickname: str = Field(..., min_length=2, max_length=20)

#응답용 스키마
class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nickname: str
