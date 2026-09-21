from app.services.analyzers.base import BaseAnalyzer
from app.schemas.analysis import AnalysisResult
import asyncio
import time

class ImageAnalyzer(BaseAnalyzer):
    async def analyze(self, file_path: str, content_type: str) -> AnalysisResult:
        # Mock processing time
        start_time = time.time()
        await asyncio.sleep(1.0) 
        
        processing_time = int((time.time() - start_time) * 1000)

        # Mock result for Image
        return AnalysisResult(
            prediction="fake",
            confidence=0.92,
            model_name="MockImageModel",
            model_version="1.0.0",
            evidence={
                "heatmap_url": "/mock_heatmap_image.png",
                "manipulated_regions": [{"x": 100, "y": 150, "width": 50, "height": 50}],
                "metadata_analysis": {"software": "Adobe Photoshop 2024", "modified": True}
            },
            processing_time_ms=processing_time
        )
