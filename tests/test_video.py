import pytest
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "version" in data


def test_health_check():
    response = client.get("/api/v1/video/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_get_stream_invalid_id():
    response = client.get("/api/v1/video/stream?video_id=invalid")
    assert response.status_code == 400


def test_get_stream_valid_id():
    test_id = "dQw4w9WgXcQ"
    response = client.get(f"/api/v1/video/stream?video_id={test_id}")
    assert response.status_code == 200
    data = response.json()
    assert "url" in data
    assert data["video_id"] == test_id


def test_get_video_info():
    test_id = "dQw4w9WgXcQ"
    response = client.get(f"/api/v1/video/info?video_id={test_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["video_id"] == test_id
    assert "title" in data
