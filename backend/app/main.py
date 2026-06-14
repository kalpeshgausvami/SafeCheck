import time
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response, status, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
from app.core.config import settings
from app.core.rate_limit import RateLimitMiddleware
from app.database.session import engine
from app.models.base import Base
from app.api import auth, jobs, results, health, billing, workspace, developer
from app.intelligence.api import router as intelligence_router
from app.trust_safety.api import router as ts_router

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# Lifespan setup for database tables auto-creation on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing database tables on startup...")
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables initialized successfully.")
    except Exception as e:
        logger.critical(f"Database initialization failed on startup: {str(e)}")
    
    yield
    
    logger.info("Shutting down engine...")
    await engine.dispose()
    logger.info("Engine disposed.")

# Initialize FastAPI app
app = FastAPI(
    title="Reel Truth Checker API",
    description="Backend API for downloading, transcribing, and fact-checking Instagram Reels using AI.",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS configuration
allowed_origins_str = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")
allowed_origins = [origin.strip() for origin in allowed_origins_str.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate Limiting Middleware
app.add_middleware(RateLimitMiddleware, limit=120, window=60)

# Custom Request Logging Middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    method = request.method
    path = request.url.path
    
    logger.info(f"Incoming Request: {method} {path}")
    
    try:
        response = await call_next(request)
        process_time = (time.time() - start_time) * 1000
        logger.info(
            f"Completed Request: {method} {path} - Status: {response.status_code} - Duration: {process_time:.2f}ms"
        )
        return response
    except Exception as e:
        process_time = (time.time() - start_time) * 1000
        logger.error(
            f"Failed Request: {method} {path} - Error: {str(e)} - Duration: {process_time:.2f}ms"
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal Server Error occurred during request processing."}
        )

from app.core.exceptions import (
    validation_exception_handler,
    http_exception_handler,
    generic_exception_handler
)
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

# Register Global Exception Handlers
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Include Routers
app.include_router(auth.router, prefix="/api")
app.include_router(jobs.router, prefix="/api")
app.include_router(results.router, prefix="/api")
app.include_router(health.router, prefix="/api")
app.include_router(billing.router, prefix="/api")
app.include_router(workspace.router, prefix="/api")
app.include_router(developer.router)
app.include_router(intelligence_router)
app.include_router(ts_router, prefix="/api")

# Hook up POST /api/analyze directly at /api/analyze level for custom mapping
@app.post("/api/analyze", response_model=jobs.JobResponse, tags=["Analysis Jobs"], status_code=status.HTTP_202_ACCEPTED)
async def analyze_reel_root(job_in: jobs.JobCreate, request: Request, db = Depends(jobs.get_db)):
    # Redirects to standard router logic
    return await jobs.analyze_reel(job_in, db)

# Root Index Endpoint
@app.get("/", tags=["Index"])
async def index():
    return {
        "app": "Reel Truth Checker API",
        "version": "1.0.0",
        "documentation": "/docs",
        "health": "/api/health"
    }
