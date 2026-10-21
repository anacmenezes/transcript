
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class TranscriptionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    filename: str
    media_type: str
    transcript_text: str
    created_at: datetime


class TranscriptionListResponse(BaseModel):
    items: list[TranscriptionResponse]
    total: int