import uuid
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.job import AnalysisJob
from app.models.result import AnalysisResult

class JobService:
    @staticmethod
    async def create_job(db: AsyncSession, reel_url: str, user_id: Optional[uuid.UUID] = None) -> AnalysisJob:
        job = AnalysisJob(
            user_id=user_id,
            reel_url=reel_url,
            status="queued",
            progress=0,
            current_step="Queued"
        )
        db.add(job)
        await db.commit()
        await db.refresh(job)

        # Trigger Celery Task
        # Import inside function to avoid circular imports
        from app.workers.tasks import analyze_reel_task
        analyze_reel_task.delay(str(job.id), reel_url)

        return job

    @staticmethod
    async def get_job(db: AsyncSession, job_id: uuid.UUID) -> Optional[AnalysisJob]:
        result = await db.execute(select(AnalysisJob).filter(AnalysisJob.id == job_id))
        return result.scalars().first()

    @staticmethod
    async def get_result(db: AsyncSession, job_id: uuid.UUID) -> Optional[AnalysisResult]:
        result = await db.execute(select(AnalysisResult).filter(AnalysisResult.job_id == job_id))
        return result.scalars().first()

job_service = JobService()
