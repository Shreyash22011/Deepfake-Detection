import pytest
from app.services.analyzers.image_analyzer import ImageAnalyzer
from app.services.analyzers.video_analyzer import VideoAnalyzer
from app.services.analyzers.audio_analyzer import AudioAnalyzer
from app.schemas.analysis import AnalysisResult

@pytest.mark.asyncio
async def test_image_analyzer():
    analyzer = ImageAnalyzer()
    result = await analyzer.analyze("dummy.jpg", "image/jpeg")
    assert isinstance(result, AnalysisResult)
    assert result.prediction == "fake"
    assert result.confidence == 0.92
    assert "heatmap_url" in result.evidence

@pytest.mark.asyncio
async def test_video_analyzer():
    analyzer = VideoAnalyzer()
    result = await analyzer.analyze("dummy.mp4", "video/mp4")
    assert isinstance(result, AnalysisResult)
    assert result.prediction == "fake"
    assert "suspicious_frames" in result.evidence

@pytest.mark.asyncio
async def test_audio_analyzer():
    analyzer = AudioAnalyzer()
    result = await analyzer.analyze("dummy.mp3", "audio/mpeg")
    assert isinstance(result, AnalysisResult)
    assert result.prediction == "real"
    assert result.confidence == 0.95
