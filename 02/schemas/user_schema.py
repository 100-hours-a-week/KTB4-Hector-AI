from pydantic import BaseModel, Field, ConfigDict


class NicknameUpdateRequest(BaseModel):
    nickname: str = Field(..., min_length=2, max_length=20)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nickname: str
