from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import os
from pathlib import Path
from dotenv import load_dotenv

# Force load .env file from backend directory
backend_dir = Path(__file__).parent.parent.parent  # Navigate to backend/
env_path = backend_dir / ".env"
if env_path.exists():
    load_dotenv(env_path)
    print(f"✅ Loaded .env from {env_path}")


class Settings(BaseSettings):
    """Application configuration settings"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )
    
    # Application
    APP_NAME: str = "Utility Server API"
    APP_VERSION: str = "1.0.0"
    API_PREFIX: str = "/api/v1"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 4
    
    # Database Configuration (Smart Detection)
    DB_USER: str = "utility_user"
    DB_PASSWORD: str = "your_password_here"
    DB_NAME: str = "utility_db"
    DB_PORT: int = 5432
    
    @property
    def DATABASE_URL(self) -> str:
        """
        Smart database URL detection:
        - Inside Docker (Production): Use internal 'postgres' hostname
        - Outside Docker (Development): Use VPS public IP
        
        This allows zero-config deployment:
        - Local: postgresql://user:pass@165.99.59.47:5432/db
        - Production: postgresql://user:pass@postgres:5432/db
        """
        # Check if running inside Docker container
        is_docker = os.path.exists('/.dockerenv') or os.path.exists('/run/.containerenv')
        
        if is_docker:
            # Production - use Docker internal network
            db_host = "postgres"
            print(f"🐳 Running in Docker - Using internal DB: {db_host}")
        else:
            # Development - use VPS public IP
            db_host = os.getenv("DB_HOST", "165.99.59.47")
            print(f"💻 Running on localhost - Using remote DB: {db_host}")
        
        connection_string = f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{db_host}:{self.DB_PORT}/{self.DB_NAME}"
        return connection_string
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_PASSWORD: Optional[str] = None
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-this"
    JWT_SECRET_KEY: str = "jwt-secret-key-change-this"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
    
    # CORS
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:5173",  # Vite dev server
        "http://localhost:8000",
        "http://127.0.0.1:5173",
    ]
    
    # File Upload
    MAX_UPLOAD_SIZE: int = 52428800  # 50MB
    UPLOAD_DIR: str = "./uploads"
    TEMP_DIR: str = "./temp"
    ALLOWED_IMAGE_EXTENSIONS: list = ["jpg", "jpeg", "png", "gif", "bmp", "webp"]
    ALLOWED_DOCUMENT_EXTENSIONS: list = ["pdf", "doc", "docx", "txt"]
    
    # Face Recognition
    FACE_RECOGNITION_TOLERANCE: float = 0.6
    FACE_DETECTION_MODEL: str = "hog"  # or "cnn" for GPU
    MAX_FACE_DISTANCE: float = 0.6
    FACE_ENCODINGS_DIR: str = "./models/faces"
    
    # OCR Configuration
    OCR_LANGUAGES: str = "eng+vie"
    TESSERACT_CMD: Optional[str] = None
    
    # OCR Provider Priority (comma-separated, first = highest priority)
    # Options: "adobe" (best quality), "tesseract" (free, unlimited)
    # Default: "tesseract,adobe" = Try Tesseract first (free), fallback to Adobe
    OCR_PRIORITY: str = "tesseract,adobe"  # User can change to "adobe,tesseract"
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000
    
    # Celery
    CELERY_BROKER_URL: Optional[str] = None
    CELERY_RESULT_BACKEND: Optional[str] = None
    
    # Email (optional)
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAIL_FROM: Optional[str] = None
    
    # Monitoring
    ENABLE_METRICS: bool = True
    ENABLE_SENTRY: bool = False
    SENTRY_DSN: Optional[str] = None
    
    # Adobe PDF Services API
    USE_ADOBE_PDF_API: bool = False
    PDF_SERVICES_CLIENT_ID: Optional[str] = None
    PDF_SERVICES_CLIENT_SECRET: Optional[str] = None
    ADOBE_ORG_ID: Optional[str] = None
    
    # Google Gemini AI
    USE_GEMINI_API: bool = False
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-1.5-flash"  # or gemini-1.5-pro
    
    # Anthropic Claude AI
    USE_CLAUDE_API: bool = False
    ANTHROPIC_API_KEY: Optional[str] = None
    
    # Technology Priority Settings (comma-separated, first = highest priority)
    # Format: "adobe,pypdf" = Try Adobe first, fallback to pypdf
    # Operations that support multiple technologies:
    COMPRESS_PRIORITY: str = "adobe,pypdf"      # Compress PDF
    WATERMARK_PRIORITY: str = "adobe,pypdf"     # Add watermark
    PDF_INFO_PRIORITY: str = "adobe,pypdf"      # Get PDF properties
    
    # Adobe-only operations (no fallback available):
    # - OCR_PDF: Convert scanned PDF to searchable (Adobe only)
    # - EXTRACT_CONTENT: AI extraction of tables/images (Adobe only)
    # - HTML_TO_PDF: Convert HTML to PDF (Adobe only)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Create directories if not exist
        os.makedirs(self.UPLOAD_DIR, exist_ok=True)
        os.makedirs(self.TEMP_DIR, exist_ok=True)
        os.makedirs(self.FACE_ENCODINGS_DIR, exist_ok=True)
        
        # Set Celery URLs if not provided
        if not self.CELERY_BROKER_URL:
            self.CELERY_BROKER_URL = self.REDIS_URL
        if not self.CELERY_RESULT_BACKEND:
            self.CELERY_RESULT_BACKEND = self.REDIS_URL
    
    def get_technology_priority(self, operation: str) -> list[str]:
        """
        Get technology priority list for an operation
        
        Args:
            operation: Operation name (compress, watermark, pdf_info)
        
        Returns:
            List of technologies in priority order, e.g., ['adobe', 'pypdf']
        
        Example:
            >>> settings.get_technology_priority('compress')
            ['adobe', 'pypdf']  # Try Adobe first, fallback to pypdf
        """
        operation_map = {
            'compress': self.COMPRESS_PRIORITY,
            'watermark': self.WATERMARK_PRIORITY,
            'pdf_info': self.PDF_INFO_PRIORITY,
        }
        
        priority_str = operation_map.get(operation, 'adobe,pypdf')
        return [tech.strip() for tech in priority_str.split(',') if tech.strip()]
    
    def should_use_adobe_first(self, operation: str) -> bool:
        """
        Check if Adobe should be tried first for an operation
        
        Args:
            operation: Operation name (compress, watermark, pdf_info)
        
        Returns:
            True if Adobe is first priority, False otherwise
        """
        priorities = self.get_technology_priority(operation)
        return len(priorities) > 0 and priorities[0].lower() == 'adobe'
    
    def get_fallback_technology(self, operation: str, failed_tech: str) -> Optional[str]:
        """
        Get next fallback technology after one fails
        
        Args:
            operation: Operation name
            failed_tech: Technology that just failed
        
        Returns:
            Next technology to try, or None if no fallback
        
        Example:
            >>> settings.get_fallback_technology('compress', 'adobe')
            'pypdf'  # Try pypdf after Adobe failed
        """
        priorities = self.get_technology_priority(operation)
        try:
            current_index = priorities.index(failed_tech.lower())
            if current_index + 1 < len(priorities):
                return priorities[current_index + 1]
        except (ValueError, IndexError):
            pass
        return None


# Create settings instance
settings = Settings()
