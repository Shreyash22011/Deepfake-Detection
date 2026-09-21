from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from enum import Enum
from datetime import datetime

class AnalysisStatus(str, Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    error = "error"

class AnalysisResult(BaseModel):
    prediction: str = Field(..., description="real | fake | synthetic | uncertain")
    confidence: float = Field(..., description="Confidence score from 0.0 to 1.0")
    model_name: str = Field(..., description="Name of the model used")
    model_version: str = Field(..., description="Version of the model")
    evidence: Dict[str, Any] = Field(default_factory=dict, description="Modality-specific evidence (e.g. heatmap, suspicious_frames)")
    processing_time_ms: int = Field(..., description="Processing time in milliseconds")

class AnalysisRecord(BaseModel):
    id: str = Field(..., description="Unique analysis ID (UUID)")
    filename: str = Field(..., description="Original name of the uploaded file")
    media_type: str = Field(..., description="image | video | audio")
    status: AnalysisStatus = Field(default=AnalysisStatus.pending)
    result: Optional[AnalysisResult] = None
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
