from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

class AnalysisResult(BaseModel):
    prediction: str = Field(..., description="real | fake | synthetic | uncertain")
    confidence: float = Field(..., description="Confidence score from 0.0 to 1.0")
    model_name: str = Field(..., description="Name of the model used")
    model_version: str = Field(..., description="Version of the model")
    evidence: Dict[str, Any] = Field(default_factory=dict, description="Modality-specific evidence (e.g. heatmap, suspicious_frames)")
    processing_time_ms: int = Field(..., description="Processing time in milliseconds")

class AnalyzeRequest(BaseModel):
    media_url: Optional[str] = None
    media_type: str = Field(..., description="image | video | audio")
    # For a real implementation, we would also handle file uploads (multipart/form-data)
