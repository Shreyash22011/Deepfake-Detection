import os
import uuid
from typing import Dict, Optional
from datetime import datetime
from fastapi import UploadFile, HTTPException

from app.schemas.analysis import AnalysisRecord, AnalysisStatus
from app.core.database import get_db
from app.services.analyzers.base import BaseAnalyzer
from app.services.analyzers.image_analyzer import ImageAnalyzer
from app.services.analyzers.video_analyzer import VideoAnalyzer
from app.services.analyzers.audio_analyzer import AudioAnalyzer

# Initialize analyzers
analyzers: Dict[str, BaseAnalyzer] = {
    "image": ImageAnalyzer(),
    "video": VideoAnalyzer(),
    "audio": AudioAnalyzer(),
}

# Temporary directory for uploads (in a real app, use S3/GCS or a proper temp dir)
UPLOAD_DIR = "/tmp/deepfake_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class AnalysisService:
    @staticmethod
    def _determine_media_type(content_type: str, filename: str) -> str:
        content_type = content_type.lower() if content_type else ""
        filename = filename.lower() if filename else ""
        
        if content_type.startswith("image/") or filename.endswith((".jpg", ".jpeg", ".png", ".webp")):
            return "image"
        if content_type.startswith("video/") or filename.endswith((".mp4", ".webm", ".mov", ".avi")):
            return "video"
        if content_type.startswith("audio/") or filename.endswith((".mp3", ".wav", ".ogg", ".m4a")):
            return "audio"
            
        raise HTTPException(status_code=400, detail=f"Unsupported media type for file: {filename}")

    @staticmethod
    async def process_upload(file: UploadFile) -> AnalysisRecord:
        """
        Main orchestration function:
        1. Validate & save file
        2. Create DB record
        3. Run analysis
        4. Update DB record
        5. Return record
        """
        # Determine media type
        media_type = AnalysisService._determine_media_type(file.content_type, file.filename)
        
        # Save file temporarily
        analysis_id = str(uuid.uuid4())
        file_extension = os.path.splitext(file.filename)[1]
        file_path = os.path.join(UPLOAD_DIR, f"{analysis_id}{file_extension}")
        
        try:
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
        except Exception as e:
            raise HTTPException(status_code=500, detail="Failed to save uploaded file")
            
        # Create pending record
        db = get_db()
        record = AnalysisRecord(
            id=analysis_id,
            filename=file.filename,
            media_type=media_type,
            status=AnalysisStatus.processing
        )
        
        if db is not None:
            await db.analyses.insert_one(record.model_dump())
            
        # Select analyzer
        analyzer = analyzers.get(media_type)
        if not analyzer:
            # Should theoretically never hit this due to determine_media_type
            error_msg = f"No analyzer available for media type: {media_type}"
            record.status = AnalysisStatus.error
            record.error_message = error_msg
            if db is not None:
                await db.analyses.update_one({"id": analysis_id}, {"$set": {"status": record.status, "error_message": error_msg}})
            raise HTTPException(status_code=500, detail=error_msg)
            
        # Run analysis (Awaited inline for MVP, should be background task in production)
        try:
            result = await analyzer.analyze(file_path, file.content_type)
            record.result = result
            record.status = AnalysisStatus.completed
            record.updated_at = datetime.utcnow()
            
            if db is not None:
                await db.analyses.update_one(
                    {"id": analysis_id}, 
                    {"$set": {
                        "status": record.status, 
                        "result": record.result.model_dump(),
                        "updated_at": record.updated_at
                    }}
                )
                
        except Exception as e:
            record.status = AnalysisStatus.error
            record.error_message = str(e)
            record.updated_at = datetime.utcnow()
            if db is not None:
                await db.analyses.update_one(
                    {"id": analysis_id}, 
                    {"$set": {
                        "status": record.status, 
                        "error_message": record.error_message,
                        "updated_at": record.updated_at
                    }}
                )
        finally:
            # Cleanup temp file
            if os.path.exists(file_path):
                os.remove(file_path)
                
        return record
