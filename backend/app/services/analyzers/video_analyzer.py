from app.services.analyzers.base import BaseAnalyzer
from app.schemas.analysis import AnalysisResult
import asyncio
import time

class VideoAnalyzer(BaseAnalyzer):
    async def analyze(self, file_path: str, content_type: str) -> AnalysisResult:
        # Mock processing time (longer for video)
        start_time = time.time()
        await asyncio.sleep(2.0)
        
        processing_time = int((time.time() - start_time) * 1000)

        # Mock result for Video
        return AnalysisResult(
            prediction="fake",
            confidence=0.88,
            model_name="MockVideoModel",
            model_version="1.1.0",
            evidence={
                "suspicious_frames": [12, 45, 112],
                "temporal_inconsistencies": "Found unnatural face morphing between frames 40-50",
                "audio_visual_sync": "0.15s delay detected"
            },
            processing_time_ms=processing_time
        )
