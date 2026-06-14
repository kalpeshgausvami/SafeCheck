from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text
from redis import Redis
from app.database.session import get_db
from app.core.config import settings
import logging
import time
import os

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/health", tags=["System Health"])

STARTUP_TIME = time.time()

@router.get("", status_code=status.HTTP_200_OK)
async def health_check(db: AsyncSession = Depends(get_db)):
    # Calculate Uptime
    uptime = round(time.time() - STARTUP_TIME, 1)
    
    # Process Telemetry
    memory_mb = 0.0
    cpu_percent = 0.0
    try:
        import psutil
        process = psutil.Process(os.getpid())
        memory_mb = round(process.memory_info().rss / (1024 * 1024), 1)
        cpu_percent = psutil.cpu_percent(interval=None)
    except Exception:
        pass

    health_status = {
        "status": "healthy",
        "database": "unreachable",
        "redis": "unreachable",
        "celery": "unreachable",
        "system_telemetry": {
            "uptime_seconds": uptime,
            "memory_usage_mb": memory_mb,
            "cpu_percent": cpu_percent,
            "process_id": os.getpid()
        }
    }
    
    # 1. Test Database
    try:
        await db.execute(text("SELECT 1"))
        health_status["database"] = "connected"
    except Exception as e:
        logger.error(f"Database healthcheck failed: {str(e)}")
        health_status["status"] = "unhealthy"
        health_status["database"] = f"error: {str(e)}"

    # 2. Test Redis
    try:
        # Connect to redis using standard sync client for health check
        redis_client = Redis.from_url(settings.REDIS_URL, socket_timeout=2)
        if redis_client.ping():
            health_status["redis"] = "connected"
    except Exception as e:
        logger.error(f"Redis healthcheck failed: {str(e)}")
        health_status["status"] = "unhealthy"
        health_status["redis"] = f"error: {str(e)}"

    # 3. Test Celery workers (ping worker count)
    try:
        from app.workers.celery_app import celery_app
        # Inspect active workers
        inspector = celery_app.control.inspect(timeout=1.0)
        active_workers = inspector.active()
        if active_workers is not None:
            health_status["celery"] = f"active workers: {len(active_workers)}"
        else:
            health_status["celery"] = "no active workers found"
    except Exception as e:
        logger.error(f"Celery healthcheck failed: {str(e)}")
        # We don't mark overall status unhealthy solely on Celery worker inspect failures
        # (e.g. if running in development mode without docker-compose worker container).
        health_status["celery"] = f"inspect error: {str(e)}"

    return health_status
