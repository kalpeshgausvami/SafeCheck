from datetime import datetime
import uuid
from typing import Optional
from pydantic import BaseModel, HttpUrl, field_validator

class JobCreate(BaseModel):
    reel_url: str

    @field_validator('reel_url')
    @classmethod
    def validate_instagram_url(cls, v: str) -> str:
        if not v.startswith(('http://', 'https://')):
            raise ValueError('URL must start with http:// or https://')
        if 'instagram.com' not in v:
            raise ValueError('URL must be an Instagram link')
        return v

class JobResponse(BaseModel):
    job_id: uuid.UUID
    status: str

    class Config:
        from_attributes = True

class JobProgressResponse(BaseModel):
    job_id: uuid.UUID
    status: str
    progress: int
    current_step: str

    class Config:
        from_attributes = True
