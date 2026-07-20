from fastapi import APIRouter, Query
from app.models.video import StreamResponse, HealthResponse
from app.services.video_service import video_service
from app.core.config import get_settings
import yt_dlp

router = APIRouter(prefix="/video", tags=["video"])


@router.get("/stream", response_model=StreamResponse)
async def get_stream(
    video_id: str = Query(..., description="YouTube Video ID", min_length=11, max_length=11)
):
    result = video_service.get_stream_url(video_id)
    return StreamResponse(
        url=result["url"],
        video_id=result["video_id"],
        format=result.get("format", "720p")
    )


@router.get("/embed")
async def get_embed(
    video_id: str = Query(..., description="YouTube Video ID", min_length=11, max_length=11)
):
    return video_service.get_embed_info(video_id)


@router.get("/info")
async def get_video_info(
    video_id: str = Query(..., description="YouTube Video ID", min_length=11, max_length=11)
):
    try:
        result = video_service.get_stream_url(video_id)
        return {
            "video_id": result["video_id"],
            "title": result.get("title"),
            "duration": result.get("duration"),
            "resolution": result.get("resolution"),
            "url": result["url"]
        }
    except Exception:
        return video_service.get_embed_info(video_id)


@router.get("/formats")
async def get_available_formats(
    video_id: str = Query(..., description="YouTube Video ID", min_length=11, max_length=11)
):
    formats = video_service.get_available_formats(video_id)
    return {"video_id": video_id, "formats": formats}


@router.get("/health", response_model=HealthResponse)
async def health_check():
    settings = get_settings()
    return HealthResponse(
        status="healthy",
        version=settings.APP_VERSION,
        yt_dlp_version=yt_dlp.version.__version__
    )
