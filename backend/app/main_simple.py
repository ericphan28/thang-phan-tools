"""Minimal FastAPI app for testing"""
# Fix Windows console encoding for Unicode emojis in logs
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.api.v1.endpoints import auth, users, roles, activity_logs, documents, images, ocr, ocr_compare, ai_admin
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
    version="2.1.0"  # Optimized Docker image (2GB → ~700MB)
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

# CORS middleware - Must be added FIRST
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
app.include_router(ai_admin.router, prefix=f"{settings.API_PREFIX}/ai-admin", tags=["🔑 AI Admin"])
app.include_router(settings_router.router, prefix=f"{settings.API_PREFIX}/settings", tags=["⚙️ Settings & Configuration"])
app.include_router(mau_2c.router, tags=["📋 Mẫu 2C - Sơ Yếu Lý Lịch"])

@app.get("/")
async def root():
    return {"message": "Utility Server API is running"}

@app.get("/health")
async def health():
    return {"status": "healthy", "version": app.version}

