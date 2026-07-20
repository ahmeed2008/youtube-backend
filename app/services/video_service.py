import subprocess
import yt_dlp
from typing import Optional
from app.core.config import get_settings
from app.core.exceptions import (
    InvalidVideoIdException,
    VideoNotFoundError,
    StreamExtractionError,
    TimeoutException
)
from app.utils.logger import logger


class VideoService:
    def __init__(self):
        self.settings = get_settings()
    
    def validate_video_id(self, video_id: str) -> bool:
        import re
        pattern = r'^[a-zA-Z0-9_-]{11}$'
        return bool(re.match(pattern, video_id))
    
    def get_stream_url(self, video_id: str, format_spec: Optional[str] = None) -> dict:
        if not self.validate_video_id(video_id):
            raise InvalidVideoIdException(video_id)
        
        try:
            url = f"https://youtu.be/{video_id}"
            
            ydl_opts = {
                'format': format_spec or self.settings.YTDLP_DEFAULT_FORMAT,
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                if not info:
                    raise VideoNotFoundError(video_id)
                
                stream_url = info.get('url')
                
                if not stream_url:
                    formats = info.get('formats', [])
                    if formats:
                        stream_url = formats[-1].get('url')
                
                if not stream_url:
                    raise StreamExtractionError(video_id)
                
                return {
                    "url": stream_url,
                    "video_id": video_id,
                    "format": info.get('format', 'unknown'),
                    "title": info.get('title', 'Unknown'),
                    "duration": info.get('duration', 0),
                    "resolution": f"{info.get('width', 0)}x{info.get('height', 0)}"
                }
                
        except yt_dlp.utils.DownloadError as e:
            error_msg = str(e)
            if "Video unavailable" in error_msg:
                raise VideoNotFoundError(video_id)
            elif "Timeout" in error_msg:
                raise TimeoutException(video_id)
            else:
                raise StreamExtractionError(video_id, error_msg)
    
    def get_available_formats(self, video_id: str) -> list:
        if not self.validate_video_id(video_id):
            raise InvalidVideoIdException(video_id)
        
        try:
            url = f"https://youtu.be/{video_id}"
            
            ydl_opts = {
                'listformats': True,
                'quiet': True,
                'no_warnings': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return info.get('formats', [])
                
        except Exception as e:
            raise StreamExtractionError(video_id, str(e))


video_service = VideoService()
