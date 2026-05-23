from pydantic import BaseModel


class SummaryResponse(BaseModel):
    target_type: str
    target_id: int
    model: str
    summary: str
