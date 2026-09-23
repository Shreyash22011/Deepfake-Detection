from app.services.analyzers.base import BaseAnalyzer
from app.schemas.analysis import AnalysisResult
import asyncio
import sys
import os

# Ensure the root project directory is in the Python path so we can import ml module
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
if root_dir not in sys.path:
    sys.path.append(root_dir)

from ml.video.inference import run_inference

class VideoAnalyzer(BaseAnalyzer):
    async def analyze(self, file_path: str, content_type: str) -> AnalysisResult:
        # Run inference in a threadpool to avoid blocking the asyncio event loop
        # since PyTorch and OpenCV operations are synchronous CPU/GPU bound.
        loop = asyncio.get_running_loop()
        
        # Determine the path to config.yaml relative to ml module
        config_path = os.path.join(root_dir, "ml", "video", "finetune_config.yaml")
        checkpoint_path = os.path.join(root_dir, "ml", "video", "checkpoints", "best_finetuned_model.pth")
        
        result_dict = await loop.run_in_executor(
            None, 
            lambda: run_inference(file_path, checkpoint_path=checkpoint_path, config_path=config_path)
        )

        if result_dict.get("prediction") == "error":
            raise RuntimeError(result_dict.get("error", "Unknown inference error"))

        return AnalysisResult(
            prediction=result_dict.get("prediction", "uncertain"),
            confidence=result_dict.get("confidence", 0.0),
            model_name=result_dict.get("model_name", "UnknownModel"),
            model_version=result_dict.get("model_version", "unknown"),
            evidence=result_dict.get("evidence", {}),
            processing_time_ms=result_dict.get("processing_time_ms", 0)
        )
