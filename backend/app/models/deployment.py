from sqlalchemy import Column, Integer, String, Float, JSON, DateTime, Enum
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class DeploymentStatus(str, enum.Enum):
    PENDING = "pending"
    GIT_PUSH = "git_push"
    BUILDING = "building"
    PULLING = "pulling"
    RESTARTING = "restarting"
    VERIFYING = "verifying"
    SUCCESS = "success"
    FAILED = "failed"


class Deployment(Base):
    __tablename__ = "deployments"

    id = Column(Integer, primary_key=True, index=True)
    version = Column(String, nullable=False, index=True)
    status = Column(Enum(DeploymentStatus), default=DeploymentStatus.PENDING, nullable=False)
    git_commit = Column(String, nullable=True)
    deploy_type = Column(String, default="force")  # "force" or "watchtower"
    
    # Phase timings in seconds
    phase_timings = Column(JSON, default={})  # {"git_push": 2.3, "build": 300.2, ...}
    total_time = Column(Float, nullable=True)  # Total seconds
    
    # Timestamps
    started_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Error info
    error_message = Column(String, nullable=True)
