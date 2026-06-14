import uuid
import secrets
import hashlib
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database.session import get_db
from app.services.auth_service import get_current_user
from app.models.user import User
from app.models.saas import ApiKey, ActivityLog
from app.schemas.job import JobCreate, JobResponse
from app.schemas.result import ResultResponse
from app.services.job_service import job_service
from pydantic import BaseModel

router = APIRouter(tags=["Developer API Platform"])

class KeyCreate(BaseModel):
    name: str

# Helper to verify external v1 API Key headers
async def verify_api_key(
    x_api_key: str = Header(..., description="Developer Bearer Key prefix with rtc_live_"),
    db: AsyncSession = Depends(get_db)
) -> User:
    if not x_api_key.startswith("rtc_live_"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid key format. Prefix must be rtc_live_"
        )
        
    # SHA256 Hash of key to match database index
    hashed_key = hashlib.sha256(x_api_key.encode("utf-8")).hexdigest()
    
    result = await db.execute(
        select(ApiKey, User)
        .join(User, ApiKey.user_id == User.id)
        .filter(ApiKey.key_hash == hashed_key, ApiKey.revoked_at == None)
    )
    row = result.first()
    if not row:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key is invalid or has been revoked."
        )
        
    api_key_obj, user = row
    return user

# User Console API key Management

@router.post("/api/developer/keys", status_code=status.HTTP_201_CREATED)
async def generate_key(
    key_in: KeyCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Enforce plan limits for API keys (e.g. Free plan cannot generate keys)
    if current_user.billing_plan == "free":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="API access is restricted to Team and Enterprise plan subscribers."
        )

    # Secure random key generation
    raw_token = f"rtc_live_{secrets.token_urlsafe(32)}"
    hashed_token = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()

    new_key = ApiKey(
        user_id=current_user.id,
        name=key_in.name,
        key_hash=hashed_token
    )
    db.add(new_key)
    
    log = ActivityLog(
        user_id=current_user.id,
        description=f"Generated API Key '{key_in.name}'",
        category="security"
    )
    db.add(log)
    await db.commit()
    
    # Return raw token only once
    return {
        "key_id": new_key.id,
        "name": new_key.name,
        "api_key": raw_token,
        "created_at": new_key.created_at
    }

@router.get("/api/developer/keys", status_code=status.HTTP_200_OK)
async def list_keys(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(ApiKey).filter(ApiKey.user_id == current_user.id))
    keys = result.scalars().all()
    
    return [
        {
            "key_id": k.id,
            "name": k.name,
            "created_at": k.created_at,
            "revoked": k.revoked_at is not None
        }
        for k in keys
    ]

@router.delete("/api/developer/keys/{key_id}", status_code=status.HTTP_200_OK)
async def revoke_key(
    key_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(ApiKey).filter(ApiKey.id == key_id, ApiKey.user_id == current_user.id)
    )
    key = result.scalars().first()
    if not key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Key index not found."
        )
        
    key.revoked_at = datetime.now(timezone.utc)
    
    log = ActivityLog(
        user_id=current_user.id,
        description=f"Revoked API Key '{key.name}'",
        category="security"
    )
    db.add(log)
    await db.commit()
    
    return {"status": "revoked", "key_id": key_id}

# Public Developer Endpoints mounted at /v1/

@router.post("/v1/analyze", response_model=JobResponse, status_code=status.HTTP_202_ACCEPTED)
async def external_analyze(
    job_in: JobCreate,
    db: AsyncSession = Depends(get_db),
    api_user: User = Depends(verify_api_key)
):
    # Enforce usage limits
    if api_user.monthly_analyses_used >= api_user.monthly_analyses_limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Monthly analysis quota exceeded. Please upgrade plan in dashboard."
        )
        
    # Queue job
    job = await job_service.create_job(db, reel_url=job_in.reel_url, user_id=api_user.id)
    
    # Increment counters
    api_user.monthly_analyses_used += 1
    api_user.api_calls_used += 1
    
    # Log usage Activity
    log = ActivityLog(
        user_id=api_user.id,
        description=f"Automated API analysis triggered for {job_in.reel_url}",
        category="analysis"
    )
    db.add(log)
    await db.commit()
    
    return {"job_id": job.id, "status": job.status}

@router.get("/v1/result/{job_id}", response_model=ResultResponse)
async def external_result(
    job_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    api_user: User = Depends(verify_api_key)
):
    job = await job_service.get_job(db, job_id)
    if not job or job.user_id != api_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job result index not found."
        )
        
    if job.status != "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Report processing in progress. Status: {job.status}"
        )
        
    result = await job_service.get_result(db, job_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Report payload missing."
        )
        
    # Increment API calls counter
    api_user.api_calls_used += 1
    await db.commit()
    
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

@router.get("/v1/usage", status_code=status.HTTP_200_OK)
async def external_usage(
    api_user: User = Depends(verify_api_key)
):
    return {
        "user_email": api_user.email,
        "billing_plan": api_user.billing_plan,
        "monthly_analyses_used": api_user.monthly_analyses_used,
        "monthly_analyses_limit": api_user.monthly_analyses_limit,
        "api_calls_used": api_user.api_calls_used
    }
