from fastapi import APIRouter
from app.schemas.analysis import AnalysisResult, AnalyzeRequest
import time

router = APIRouter()

@router.post("/analyze", response_model=AnalysisResult)
def analyze_media(request: AnalyzeRequest):
    # This is a mock response. In a real scenario, this would call
    # the appropriate ml service (image/video/audio) based on request.media_type
    
    # Simulate processing time
    time.sleep(0.5)
    
    return AnalysisResult(
        prediction="fake",
        confidence=0.85,
        model_name="mock_v1",
        model_version="1.0",
        evidence={
            "suspicious_regions": [[10, 20, 50, 60]],
            "note": "This is placeholder evidence."
        },
        processing_time_ms=500
    )
