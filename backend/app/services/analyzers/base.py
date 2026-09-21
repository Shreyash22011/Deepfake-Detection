from abc import ABC, abstractmethod
from app.schemas.analysis import AnalysisResult

class BaseAnalyzer(ABC):
    """
    Abstract base class for all modality analyzers (image, video, audio).
    """

    @abstractmethod
    async def analyze(self, file_path: str, content_type: str) -> AnalysisResult:
        """
        Analyze the media file and return the result.
        
        Args:
            file_path: The local temporary path to the uploaded file.
            content_type: The MIME type of the file.
            
        Returns:
            AnalysisResult containing prediction, confidence, and evidence.
        """
        pass
