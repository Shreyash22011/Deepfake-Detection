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
async def test_video_analyzer(monkeypatch):
    # Mock the ml.video.inference.run_inference to avoid needing a real video file
    def mock_run_inference(video_path, checkpoint_path=None, config_path=None):
        return {
            "prediction": "fake",
            "confidence": 0.88,
            "model_name": "resnet18_LSTM",
            "model_version": "1.0.0-prototype",
            "evidence": {"suspicious_frames": [1, 2, 3]},
            "processing_time_ms": 100
        }
        
    import app.services.analyzers.video_analyzer
    monkeypatch.setattr(app.services.analyzers.video_analyzer, "run_inference", mock_run_inference)
    
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
