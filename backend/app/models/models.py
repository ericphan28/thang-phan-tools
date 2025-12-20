from sqlalchemy import Column, Integer, String, DateTime, Float, Text, Boolean, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ARRAY
from datetime import datetime
from app.core.database import Base


# Import User and Role from auth_models to avoid duplicates
from app.models.auth_models import User, Role, Permission


class APILog(Base):
    """API usage logging"""
    __tablename__ = "api_logs"
    __table_args__ = {"extend_existing": True}
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    endpoint = Column(String, nullable=False, index=True)
    method = Column(String, nullable=False)
    status_code = Column(Integer, nullable=False)
    duration_ms = Column(Float, nullable=False)  # Request duration in milliseconds
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    user = relationship("User")


class ProcessedFile(Base):
    """Track processed files"""
    __tablename__ = "processed_files"
    __table_args__ = {"extend_existing": True}
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    file_type = Column(String, nullable=False)  # image, document, etc.
    operation = Column(String, nullable=False)  # resize, ocr, convert, etc.
    original_filename = Column(String, nullable=False)
    processed_filename = Column(String, nullable=True)
    file_size = Column(Integer, nullable=False)  # in bytes
    processing_time_ms = Column(Float, nullable=False)
    status = Column(String, default="completed")  # completed, failed, processing
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


class APIKey(Base):
    """API Keys for authentication"""
    __tablename__ = "api_keys"
    __table_args__ = {"extend_existing": True}
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    key = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)  # Key description
    is_active = Column(Boolean, default=True)
    last_used_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User")


class AIProviderKey(Base):
    """AI Provider API Keys (Gemini, Claude, Adobe, etc.)"""
    __tablename__ = "ai_provider_keys"
    __table_args__ = {"extend_existing": True}
    
    id = Column(Integer, primary_key=True, index=True)
    provider = Column(String, nullable=False, index=True)  # gemini, claude, adobe
    key_name = Column(String, nullable=False)  # Display name
    api_key = Column(String, nullable=False)  # Encrypted key
    org_id = Column(String, nullable=True)  # For providers that need org ID (Adobe)
    client_id = Column(String, nullable=True)  # For OAuth providers
    client_secret = Column(String, nullable=True)  # For OAuth providers
    is_active = Column(Boolean, default=True)
    is_primary = Column(Boolean, default=False)  # Primary key for this provider
    monthly_limit = Column(Float, nullable=True)  # Monthly spending limit in USD
    rate_limit_rpm = Column(Integer, nullable=True)  # Requests per minute limit
    last_used_at = Column(DateTime, nullable=True)
    last_error = Column(Text, nullable=True)
    error_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    usage_logs = relationship("AIUsageLog", back_populates="provider_key")


class AIUsageLog(Base):
    """Track AI API usage for billing and monitoring"""
    __tablename__ = "ai_usage_logs"
    __table_args__ = {"extend_existing": True}
    
    id = Column(Integer, primary_key=True, index=True)
    provider_key_id = Column(Integer, ForeignKey("ai_provider_keys.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Request info
    operation = Column(String, nullable=False, index=True)  # ocr, chat, vision, etc.
    model = Column(String, nullable=False)  # gemini-2.5-flash, claude-sonnet-4, etc.
    request_id = Column(String, nullable=True)  # Provider's request ID
    
    # Token usage
    input_tokens = Column(Integer, default=0)
    output_tokens = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    
    # Cost (in USD)
    input_cost = Column(Float, default=0.0)
    output_cost = Column(Float, default=0.0)
    total_cost = Column(Float, default=0.0)
    
    # Performance
    processing_time_ms = Column(Float, nullable=True)
    
    # Status
    status = Column(String, default="success")  # success, error, timeout
    error_message = Column(Text, nullable=True)
    
    # Metadata
    request_metadata = Column(Text, nullable=True)  # JSON string for extra info
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    provider_key = relationship("AIProviderKey", back_populates="usage_logs")


class AIBillingSummary(Base):
    """Monthly billing summary per provider"""
    __tablename__ = "ai_billing_summary"
    __table_args__ = {"extend_existing": True}
    
    id = Column(Integer, primary_key=True, index=True)
    provider = Column(String, nullable=False, index=True)  # gemini, claude, adobe
    period = Column(String, nullable=False, index=True)  # YYYY-MM format
    
    # Usage totals
    total_requests = Column(Integer, default=0)
    total_input_tokens = Column(Integer, default=0)
    total_output_tokens = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    
    # Cost totals (USD)
    total_input_cost = Column(Float, default=0.0)
    total_output_cost = Column(Float, default=0.0)
    total_cost = Column(Float, default=0.0)
    
    # Stats
    avg_response_time_ms = Column(Float, nullable=True)
    error_count = Column(Integer, default=0)
    success_rate = Column(Float, default=100.0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
