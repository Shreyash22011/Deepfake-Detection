from fastapi import APIRouter, HTTPException
from typing import List
from app.schemas.analysis import AnalysisRecord
from app.core.database import get_db

router = APIRouter()

@router.get("", response_model=List[AnalysisRecord])
async def get_analyses():
    db = get_db()
    if db is None:
        raise HTTPException(status_code=500, detail="Database connection not available")
        
    cursor = db.analyses.find().sort("created_at", -1)
    analyses = await cursor.to_list(length=100)
    return analyses

@router.get("/{analysis_id}", response_model=AnalysisRecord)
async def get_analysis(analysis_id: str):
    db = get_db()
    if db is None:
        raise HTTPException(status_code=500, detail="Database connection not available")
        
    analysis = await db.analyses.find_one({"id": analysis_id})
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
        
    return analysis
