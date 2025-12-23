from pydantic import BaseModel
from typing import Optional, Dict, List
from datetime import datetime
from app.models.deployment import DeploymentStatus as DeploymentStatusEnum


class DeploymentBase(BaseModel):
    version: str
    git_commit: Optional[str] = None
    deploy_type: str = "force"


class DeploymentCreate(DeploymentBase):
    pass


class DeploymentUpdate(BaseModel):
    status: Optional[DeploymentStatusEnum] = None
    phase_timings: Optional[Dict[str, float]] = None
    total_time: Optional[float] = None
    error_message: Optional[str] = None


class DeploymentResponse(DeploymentBase):
    id: int
    status: DeploymentStatusEnum
    phase_timings: Dict[str, float]
    total_time: Optional[float]
    started_at: datetime
    completed_at: Optional[datetime]
    error_message: Optional[str]

    class Config:
        from_attributes = True


class DeploymentListResponse(BaseModel):
    deployments: List[DeploymentResponse]
    total: int
