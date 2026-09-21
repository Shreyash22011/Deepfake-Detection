from fastapi import APIRouter, UploadFile, File
from app.schemas.analysis import AnalysisRecord
from app.services.analysis_service import AnalysisService

router = APIRouter()

@router.post("/analyze", response_model=AnalysisRecord)
async def analyze_media(file: UploadFile = File(...)):
    """
    Upload a media file (image, video, audio) for deepfake analysis.
    Returns an AnalysisRecord which contains the status and result.
    """
    record = await AnalysisService.process_upload(file)
    return record
