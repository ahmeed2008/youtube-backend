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


YDL_EXTRACTORS = [
    {
        'name': 'android',
        'opts': {
            'format': 'best[height<=720]/best',
            'extractor_args': {'youtube': {'player_client': ['android']}},
            'http_headers': {
                'User-Agent': 'com.google.android.youtube/19.02.39 (Linux; U; Android 14) gzip',
            },
        }
    },
    {
        'name': 'ios',
        'opts': {
            'format': 'best[height<=720]/best',
            'extractor_args': {'youtube': {'player_client': ['ios']}},
            'http_headers': {
                'User-Agent': 'com.google.ios.youtube/19.02.36 (iPhone16,2; U; CPU iOS 17_4_1 like Mac OS X)',
            },
        }
    },
    {
        'name': 'web',
        'opts': {
            'format': 'best[height<=720]/best',
            'extractor_args': {'youtube': {'player_client': ['web']}},
        }
    },
    {
        'name': 'web_creator',
        'opts': {
            'format': 'best[height<=720]/best',
            'extractor_args': {'youtube': {'player_client': ['web_creator']}},
        }
    },
]

BASE_OPTS = {
    'quiet': True,
    'no_warnings': True,
    'extract_flat': False,
    'socket_timeout': 30,
}


class VideoService:
    def __init__(self):
        self.settings = get_settings()

    def validate_video_id(self, video_id: str) -> bool:
        import re
        pattern = r'^[a-zA-Z0-9_-]{11}$'
        return bool(re.match(pattern, video_id))

    def _extract_with_extractor(self, url: str, extractor: dict) -> Optional[dict]:
        ydl_opts = {**BASE_OPTS, **extractor['opts']}

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if not info:
                    return None

                stream_url = info.get('url')

                if not stream_url:
                    formats = info.get('formats', [])
                    if formats:
                        stream_url = formats[-1].get('url')

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
            logger.debug(f"Extractor '{extractor['name']}' failed: {e}")
            return None

    def _try_ffmpeg_extract(self, video_id: str) -> Optional[str]:
        try:
            url = f"https://youtu.be/{video_id}"
            cmd = [
                "yt-dlp",
                "-f", "best[height<=720]/best",
                "-g",
                "--extractor-args", "youtube:player_client=android",
                url
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
        except Exception as e:
            logger.debug(f"ffmpeg fallback failed: {e}")
        return None

    def get_stream_url(self, video_id: str, format_spec: Optional[str] = None) -> dict:
        if not self.validate_video_id(video_id):
            raise InvalidVideoIdException(video_id)

        url = f"https://youtu.be/{video_id}"

        for extractor in YDL_EXTRACTORS:
            logger.info(f"Trying extractor: {extractor['name']}")
            result = self._extract_with_extractor(url, extractor)
            if result:
                result['video_id'] = video_id
                return result

        logger.info("All extractors failed, trying subprocess fallback...")
        fallback_url = self._try_ffmpeg_extract(video_id)
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
