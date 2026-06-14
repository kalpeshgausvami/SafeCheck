import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db
from app.schemas.result import ResultResponse
from app.services.job_service import job_service

router = APIRouter(prefix="/results", tags=["Analysis Results"])

@router.get("/{job_id}", response_model=ResultResponse)
async def get_analysis_result(job_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    # 1. Verify that the job is completed
    job = await job_service.get_job(db, job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis job not found"
        )
    
    if job.status != "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Analysis is not complete. Current job status: {job.status}"
        )
        
    result = await job_service.get_result(db, job_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Analysis report could not be found despite job completion"
        )
        
    # Return formatted result response
    return {
        "job_id": result.job_id,
        "verdict": job.verdict or "Uncertain",
        "confidence": job.confidence_score or 0,
        "risk_level": result.final_report.get("risk_level", "Medium"),
        "reasoning": result.llm_reasoning,
        "caption_text": result.caption_text,
        "uploader": result.final_report.get("uploader", "@unknown"),
        "duration": result.final_report.get("duration", "0:00"),
        "views": result.final_report.get("views", "0"),
        "likes": result.final_report.get("likes", "0"),
        "transcript": result.transcript,
        "ocr_text": result.ocr_text,
        "claims": result.extracted_claims,
        "sources": result.fact_check_sources
    }
