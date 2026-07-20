from pydantic import BaseModel, Field, field_validator
import re


class VideoIdRequest(BaseModel):
    video_id: str = Field(..., description="YouTube Video ID", min_length=11, max_length=11)
    
    @field_validator('video_id')
    @classmethod
    def validate_video_id(cls, v: str) -> str:
        pattern = r'^[a-zA-Z0-9_-]{11}$'
        if not re.match(pattern, v):
            raise ValueError(f"Geçersiz video ID formatı: {v}")
        return v


class StreamResponse(BaseModel):
    url: str = Field(..., description="Video stream URL'si")
    video_id: str = Field(..., description="YouTube Video ID")
    format: str = Field(default="720p", description="Video çözünürlüğü")


class ErrorResponse(BaseModel):
    detail: str = Field(..., description="Hata mesajı")
    code: int = Field(..., description="HTTP durum kodu")


class HealthResponse(BaseModel):
    status: str = Field(default="healthy")
    version: str
    yt_dlp_version: str
