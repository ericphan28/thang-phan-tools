from sqlalchemy import Column, Integer, String, DateTime, Float, Text, Boolean, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ARRAY
from datetime import datetime
from app.core.database import Base


# Many-to-Many relationship table for User and Role
user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True)
)


class User(Base):
    """User model for authentication"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    api_logs = relationship("APILog", back_populates="user")
    roles = relationship("Role", secondary=user_roles, back_populates="users")
    api_keys = relationship("APIKey", back_populates="user")


class Role(Base):
    """Role model for RBAC"""
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    users = relationship("User", secondary=user_roles, back_populates="roles")
    permissions = relationship("Permission", back_populates="role", cascade="all, delete-orphan")


class Permission(Base):
    """Permission model for fine-grained access control"""
    __tablename__ = "permissions"
    
    id = Column(Integer, primary_key=True, index=True)
    role_id = Column(Integer, ForeignKey('roles.id'), nullable=False)
    resource = Column(String, nullable=False, index=True)  # e.g., "image", "document", "user"
    action = Column(String, nullable=False, index=True)    # e.g., "read", "write", "delete"
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    role = relationship("Role", back_populates="permissions")


class APILog(Base):
    """API usage logging"""
    __tablename__ = "api_logs"
    
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
    user = relationship("User", back_populates="api_logs")


class ProcessedFile(Base):
    """Track processed files"""
    __tablename__ = "processed_files"
    
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
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    key = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)  # Key description
    is_active = Column(Boolean, default=True)
    last_used_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="api_keys")
