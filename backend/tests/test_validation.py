import pytest
from app.services.analysis_service import AnalysisService
from fastapi import HTTPException

def test_determine_media_type_image():
    assert AnalysisService._determine_media_type("image/jpeg", "test.jpg") == "image"
    assert AnalysisService._determine_media_type("application/octet-stream", "test.png") == "image"

def test_determine_media_type_video():
    assert AnalysisService._determine_media_type("video/mp4", "test.mp4") == "video"
    assert AnalysisService._determine_media_type("application/octet-stream", "test.avi") == "video"

def test_determine_media_type_audio():
    assert AnalysisService._determine_media_type("audio/mpeg", "test.mp3") == "audio"
    assert AnalysisService._determine_media_type("application/octet-stream", "test.wav") == "audio"

def test_determine_media_type_invalid():
    with pytest.raises(HTTPException):
        AnalysisService._determine_media_type("application/pdf", "test.pdf")
