from fastapi import HTTPException, status


class VideoServiceException(HTTPException):
    def __init__(self, detail: str, status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR):
        super().__init__(status_code=status_code, detail=detail)


class InvalidVideoIdException(VideoServiceException):
    def __init__(self, video_id: str):
        super().__init__(
            detail=f"Geçersiz video ID: {video_id}",
            status_code=status.HTTP_400_BAD_REQUEST
        )


class VideoNotFoundError(VideoServiceException):
    def __init__(self, video_id: str):
        super().__init__(
            detail=f"Video bulunamadı: {video_id}",
            status_code=status.HTTP_404_NOT_FOUND
        )


class StreamExtractionError(VideoServiceException):
    def __init__(self, video_id: str, error: str = None):
        detail = f"Stream URL extract edilemedi: {video_id}"
        if error:
            detail += f" - {error}"
        super().__init__(
            detail=detail,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )


class RateLimitExceeded(VideoServiceException):
    def __init__(self):
        super().__init__(
            detail="Çok fazla istek. Lütfen bekleyin.",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS
        )


class TimeoutException(VideoServiceException):
    def __init__(self, video_id: str):
        super().__init__(
            detail=f"Video işlenirken zaman aşımı: {video_id}",
            status_code=status.HTTP_408_REQUEST_TIMEOUT
        )
