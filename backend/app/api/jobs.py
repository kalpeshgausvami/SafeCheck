import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db
from app.schemas.job import JobCreate, JobResponse, JobProgressResponse
from app.services.job_service import job_service

router = APIRouter(prefix="/jobs", tags=["Analysis Jobs"])

# Standard POST endpoint as requested: POST /api/analyze (routed to /api/analyze at main app level)
# Let's map it under APIRouter prefix to support modularity, but we'll include helper routes.
# The user wants "POST /api/analyze" which we can hook up at the app root level or via APIRouter.
# We will define a root-linked function or configure router mapping correctly.
# In main.py, we can include this router and also redirect/include individual paths.
# Let's declare the standard route here:

@router.post("/analyze", response_model=JobResponse, status_code=status.HTTP_202_ACCEPTED)
async def analyze_reel(job_in: JobCreate, db: AsyncSession = Depends(get_db)):
    try:
        job = await job_service.create_job(db, reel_url=job_in.reel_url)
        return {"job_id": job.id, "status": job.status}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to queue analysis job: {str(e)}"
        )

@router.get("/{job_id}", response_model=JobProgressResponse)
async def get_job_status(job_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    job = await job_service.get_job(db, job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis job not found"
        )
    return {
        "job_id": job.id,
        "status": job.status,
        "progress": job.progress,
        "current_step": job.current_step
    }
