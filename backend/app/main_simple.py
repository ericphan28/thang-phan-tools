"""Minimal FastAPI app for testing"""
# Fix Windows console encoding for Unicode emojis in logs
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from fastapi import FastAPI, Request, status

# ============ REQUEST SIZE & TIMEOUT OPTIMIZATION ============
# Increase default limits for file uploads and processing time
MAX_REQUEST_BODY_SIZE = 200 * 1024 * 1024  # 200MB for large PDFs
REQUEST_TIMEOUT = 300  # 5 minutes for large PDF processing
KEEP_ALIVE_TIMEOUT = 600  # 10 minutes keep-alive
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.api.v1.endpoints import auth, users, roles, activity_logs, documents, images, ocr, ocr_compare, ai_admin, deployment, subscription, vb_hanh_chinh, adobe_usage
from app.api.v1.endpoints import settings as settings_router
from app.routers import mau_2c
import logging
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from backend/.env
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Utility Server API",
    description="API for Authentication, User Management, Document Processing, Image Tools and OCR with AI-powered Data Visualization",
    version="2.1.5",  # Enhanced timeout configuration
    # Swagger UI config for large file uploads and long processing
    swagger_ui_parameters={
        "requestTimeout": 300000,  # 5 minutes timeout for Swagger UI
        "displayRequestDuration": True,
        "docExpansion": "none",  # Don't expand all endpoints by default
    },
)

# Add validation error handler
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Log validation errors with details"""
    logger.error(f"❌ Validation Error on {request.url}:")
    
    # Convert errors to JSON-safe format (some 'input' fields may have UploadFile objects)
    errors = []
    for error in exc.errors():
        error_dict = error.copy()
        # Convert 'input' to string if it's not JSON serializable
        if 'input' in error_dict:
            try:
                import json
                json.dumps(error_dict['input'])
            except (TypeError, ValueError):
                error_dict['input'] = str(error_dict['input'])
        errors.append(error_dict)
    
    logger.error(f"   Errors: {errors}")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": errors,
            "message": "Validation error - check your input data"
        },
    )

# Add generic exception handler
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Log all unhandled exceptions"""
    logger.error(f"❌ Unhandled exception on {request.url}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": str(exc)},
    )

# Timeout middleware for long-running operations
import asyncio
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

class TimeoutMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, timeout: int = REQUEST_TIMEOUT):
        super().__init__(app)
        self.timeout = timeout

    async def dispatch(self, request: Request, call_next):
        """Add timeout to requests, especially for file processing endpoints"""
        
        # Apply extended timeout for file processing endpoints
        if any(path in str(request.url) for path in [
            '/documents/', '/ocr/', '/convert/', '/upload/'
        ]):
            timeout = self.timeout
        else:
            timeout = 60  # 1 minute for other endpoints
            
        try:
            return await asyncio.wait_for(call_next(request), timeout=timeout)
        except asyncio.TimeoutError:
            logger.warning(f"⏰ Request timeout ({timeout}s) for {request.url}")
            return JSONResponse(
                status_code=408,
                content={
                    "detail": f"Request timed out after {timeout} seconds. Try with a smaller file or check your connection."
                }
            )

# Add timeout middleware
app.add_middleware(TimeoutMiddleware)

# CORS middleware - Must be added AFTER custom middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Temporarily allow all origins for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix=f"{settings.API_PREFIX}/auth", tags=["Authentication"])
app.include_router(users.router, prefix=f"{settings.API_PREFIX}/users", tags=["User Management"])
app.include_router(roles.router, prefix=f"{settings.API_PREFIX}/roles", tags=["Role Management"])
app.include_router(activity_logs.router, prefix=f"{settings.API_PREFIX}/logs", tags=["Activity Logs"])
app.include_router(documents.router, prefix=f"{settings.API_PREFIX}/documents", tags=["📄 Document Tools"])
app.include_router(images.router, prefix=f"{settings.API_PREFIX}/images", tags=["🎨 Image Tools"])
app.include_router(ocr.router, prefix=f"{settings.API_PREFIX}/ocr", tags=["📝 OCR - Text Recognition"])
app.include_router(ocr_compare.router, prefix=f"{settings.API_PREFIX}", tags=["🔍 OCR Comparison"])
app.include_router(vb_hanh_chinh.router, prefix=f"{settings.API_PREFIX}/vb-hanh-chinh", tags=["📋 Văn Bản Hành Chính"])
app.include_router(ai_admin.router, prefix=f"{settings.API_PREFIX}/ai-admin", tags=["🔑 AI Admin"])
app.include_router(subscription.router, prefix=f"{settings.API_PREFIX}/subscription", tags=["💳 User Subscription"])
app.include_router(settings_router.router, prefix=f"{settings.API_PREFIX}/settings", tags=["⚙️ Settings & Configuration"])
app.include_router(adobe_usage.router, prefix=f"{settings.API_PREFIX}", tags=["📊 Adobe Usage Tracking"])
app.include_router(deployment.router, prefix=f"{settings.API_PREFIX}", tags=["🚀 Deployment Monitor"])
app.include_router(mau_2c.router, tags=["📋 Mẫu 2C - Sơ Yếu Lý Lịch"])

@app.get("/")
async def root():
    return {"message": "Utility Server API is running"}

@app.get("/health")
async def health():
    return {"status": "healthy", "version": app.version}

