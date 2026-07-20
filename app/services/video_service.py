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


BASE_OPTS = {
    'quiet': True,
    'no_warnings': True,
    'extract_flat': False,
    'socket_timeout': 30,
    'no_check_certificates': True,
    'ignoreerrors': True,
}


class VideoService:
    def __init__(self):
        self.settings = get_settings()

    def validate_video_id(self, video_id: str) -> bool:
        import re
        pattern = r'^[a-zA-Z0-9_-]{11}$'
        return bool(re.match(pattern, video_id))

    def _try_extract(self, url: str, extractor_args: dict) -> Optional[dict]:
        ydl_opts = {
            **BASE_OPTS,
            'format': 'best[height<=720]/best',
            'extractor_args': extractor_args,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if not info:
                    return None

                stream_url = info.get('url')
                if not stream_url:
                    formats = info.get('formats', [])
                    for f in reversed(formats):
                        if f.get('url'):
                            stream_url = f['url']
                            break

                if not stream_url:
                    return None

                return {
                    "url": stream_url,
                    "format": info.get('format', 'unknown'),
                    "title": info.get('title', 'Unknown'),
                    "duration": info.get('duration', 0),
                    "resolution": f"{info.get('width', 0)}x{info.get('height', 0)}",
                }
        except Exception as e:
            logger.debug(f"Extract failed: {e}")
            return None

    def _try_subprocess(self, video_id: str) -> Optional[str]:
        clients = ['android', 'ios', 'web_creator', 'web']
        for client in clients:
            try:
                cmd = [
                    "yt-dlp",
                    "-f", "best[height<=720]/best",
                    "-g",
                    "--no-check-certificates",
                    "--extractor-args", f"youtube:player_client={client}",
                    f"https://youtu.be/{video_id}"
                ]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                if result.returncode == 0 and result.stdout.strip():
                    logger.info(f"Subprocess success with client: {client}")
                    return result.stdout.strip().split('\n')[0]
            except Exception as e:
                logger.debug(f"Subprocess {client} failed: {e}")
        return None

    def get_stream_url(self, video_id: str, format_spec: Optional[str] = None) -> dict:
        if not self.validate_video_id(video_id):
            raise InvalidVideoIdException(video_id)

        url = f"https://youtu.be/{video_id}"

        clients = [
            {'youtube': {'player_client': ['android']}},
            {'youtube': {'player_client': ['ios']}},
            {'youtube': {'player_client': ['web_creator']}},
            {'youtube': {'player_client': ['web']}},
            {'youtube': {'player_client': ['mweb']}},
        ]

        for extractor_args in clients:
            result = self._try_extract(url, extractor_args)
            if result:
                result['video_id'] = video_id
                return result

        fallback_url = self._try_subprocess(video_id)
        if fallback_url:
            return {
                "url": fallback_url,
                "video_id": video_id,
                "format": "720p",
                "title": "Unknown",
                "duration": 0,
                "resolution": "unknown",
            }

        raise StreamExtractionError(video_id, "All extraction methods failed")

    def get_embed_info(self, video_id: str) -> dict:
        if not self.validate_video_id(video_id):
            raise InvalidVideoIdException(video_id)

        return {
            "video_id": video_id,
            "embed_url": f"https://www.youtube.com/embed/{video_id}",
            "watch_url": f"https://www.youtube.com/watch?v={video_id}",
            "thumbnail_url": f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg",
            "oembed_url": f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json",
        }

    def get_available_formats(self, video_id: str) -> list:
        if not self.validate_video_id(video_id):
            raise InvalidVideoIdException(video_id)

        try:
            url = f"https://youtu.be/{video_id}"
            ydl_opts = {
                **BASE_OPTS,
                'listformats': True,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return info.get('formats', [])

        except Exception as e:
            raise StreamExtractionError(video_id, str(e))


video_service = VideoService()
