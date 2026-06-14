from typing import List, Dict, Any, Optional
import uuid
from pydantic import BaseModel

class TranscriptSegmentSchema(BaseModel):
    time: str
    text: str
    flagged: bool

class OCRBlockSchema(BaseModel):
    time: str
    text: str

class ExtractedClaimSchema(BaseModel):
    title: str
    rating: str
    analysis: str

class FactSourceSchema(BaseModel):
    name: str
    url: str
    snippet: str

class ResultResponse(BaseModel):
    job_id: uuid.UUID
    verdict: str
    confidence: int
    risk_level: str
    reasoning: str
    caption_text: str
    uploader: str
    duration: str
    views: str
    likes: str
    transcript: List[TranscriptSegmentSchema]
    ocr_text: List[OCRBlockSchema]
    claims: List[ExtractedClaimSchema]
    sources: List[FactSourceSchema]

    class Config:
        from_attributes = True
