import logging
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handler for Pydantic validation errors (RequestValidationError).
    """
    logger.warning(f"Validation failure on {request.url.path}: {str(exc.errors())}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "status": "error",
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Invalid request payload or query parameters.",
                "details": exc.errors()
            }
        }
    )

async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """
    Handler for explicit FastAPI/Starlette HTTPExceptions.
    """
    logger.warning(f"HTTP exception on {request.url.path} (status={exc.status_code}): {exc.detail}")
    
    # Map code based on status code
    code = "API_ERROR"
    if exc.status_code == 401:
        code = "UNAUTHORIZED"
    elif exc.status_code == 403:
        code = "FORBIDDEN"
    elif exc.status_code == 404:
        code = "NOT_FOUND"
    elif exc.status_code == 429:
        code = "RATE_LIMIT_EXCEEDED"
        
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "error": {
                "code": code,
                "message": exc.detail,
                "details": None
            }
        }
    )

async def generic_exception_handler(request: Request, exc: Exception):
    """
    Global fallback handler for unhandled server errors.
    """
    logger.critical(f"Unhandled system exception on {request.url.path}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "error",
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred on the server.",
                "details": None
            }
        }
    )
