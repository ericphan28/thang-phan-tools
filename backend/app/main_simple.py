"""Minimal FastAPI app for testing"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.endpoints import auth, users, roles, activity_logs, documents, images, ocr

app = FastAPI(
    title="Utility Server API",
    description="API for Authentication, User Management, Document Processing, Image Tools and OCR",
    version="2.0.0"
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

@app.get("/")
async def root():
    return {"message": "Utility Server API is running"}

@app.get("/health")
async def health():
    return {"status": "healthy", "version": "1.0.0"}
