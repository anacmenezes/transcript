
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from src.transcript.models.analysis import AnaliseTranscricao


class AnalysisRecordResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    transcription_id: int
    result: AnaliseTranscricao
    created_at: datetime


class AnalysisListResponse(BaseModel):
    items: list[AnalysisRecordResponse]
    total: int