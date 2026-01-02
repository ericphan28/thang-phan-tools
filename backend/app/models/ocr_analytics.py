# -*- coding: utf-8 -*-
"""
OCR Analytics Model - Logging for Sales Analytics
Tracks user behavior for conversion optimization and sales insights
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class OCRUsageLog(Base):
    """
    Log mọi thao tác OCR của người dùng → Phân tích bán hàng
    
    Sales Analytics Use Cases:
    - Conversion funnel: Upload → Process → Download → Upgrade
    - Feature usage patterns: Which file types? Average size?
    - Error tracking: Where do users fail? → Improve UX
    - Quota exhaustion: Who hits limits? → Upgrade prompts
    - Processing time: Performance bottlenecks → Optimize
    """
    __tablename__ = "ocr_usage_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    
    # File metadata (sales insight: what file types are most popular?)
    file_name = Column(String(500), nullable=False)
    file_size_bytes = Column(Integer, nullable=False)  # Track usage patterns
    file_type = Column(String(50), nullable=False)  # "pdf", "image/png", etc.
    total_pages = Column(Integer, default=1)  # Multi-page documents?
    
    # Detection results (sales insight: scanned vs text PDFs)
    detection_method = Column(String(50), nullable=True)  # "text_extraction", "image_ratio", "gemini_vision"
    is_scanned = Column(Boolean, default=False)  # Track scanned vs text-based
    
    # Processing metrics (sales insight: performance, success rate)
    processing_time_seconds = Column(Float, nullable=True)  # How fast?
    gemini_model_used = Column(String(100), nullable=True)  # Which AI model?
    tokens_used = Column(Integer, default=0)  # AI cost tracking
    cost_usd = Column(Float, default=0.0)  # Actual cost
    
    # Outcome (sales insight: success rate, error patterns)
    success = Column(Boolean, default=False)
    error_message = Column(Text, nullable=True)  # What went wrong?
    error_type = Column(String(100), nullable=True)  # "quota_exceeded", "file_too_large", "ocr_failed"
    
    # User actions (sales insight: download rate = feature value)
    downloaded = Column(Boolean, default=False)  # Did user download result?
    download_format = Column(String(20), nullable=True)  # "docx", "txt"
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationship
    user = relationship("User", back_populates="ocr_logs")


class OCRUserAction(Base):
    """
    Track chi tiết mọi action của user trong OCR workflow
    → Phân tích conversion funnel, A/B testing, UX optimization
    """
    __tablename__ = "ocr_user_actions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    session_id = Column(String(100), index=True)  # Group actions by session
    
    # Action tracking
    action_type = Column(String(100), nullable=False, index=True)  
    # Examples: "page_view", "file_upload", "detection_start", "download_result", 
    #           "upgrade_click", "quota_warning_shown", "error_occurred"
    
    action_metadata = Column(Text, nullable=True)  # JSON metadata
    # Example: {"file_count": 3, "total_size_mb": 15.2, "source": "drag_drop"}
    
    # Context
    page_url = Column(String(500), nullable=True)  # "/ocr-to-word"
    user_agent = Column(String(500), nullable=True)  # Device info
    ip_address = Column(String(50), nullable=True)  # Geographic analysis
    
    # Timing
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationship
    user = relationship("User")


class OCRConversionFunnel(Base):
    """
    Aggregated conversion metrics for sales dashboard
    Auto-updated by analytics service
    """
    __tablename__ = "ocr_conversion_funnel"
    
    id = Column(Integer, primary_key=True)
    date = Column(DateTime, nullable=False, index=True)  # Daily aggregation
    
    # Funnel stages
    total_page_views = Column(Integer, default=0)
    total_file_uploads = Column(Integer, default=0)
    total_processing_started = Column(Integer, default=0)
    total_processing_success = Column(Integer, default=0)
    total_downloads = Column(Integer, default=0)
    total_upgrade_clicks = Column(Integer, default=0)
    total_quota_exceeded = Column(Integer, default=0)
    
    # Conversion rates (calculated)
    upload_rate = Column(Float, default=0.0)  # uploads / page_views
    success_rate = Column(Float, default=0.0)  # success / processing_started
    download_rate = Column(Float, default=0.0)  # downloads / success
    upgrade_rate = Column(Float, default=0.0)  # upgrade_clicks / quota_exceeded
    
    # Revenue metrics
    new_pro_signups = Column(Integer, default=0)  # From OCR feature
    estimated_revenue_vnd = Column(Float, default=0.0)  # new_pro * 299,000
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
