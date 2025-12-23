"""Deployment monitoring endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.core.database import get_db
from app.models.deployment import Deployment, DeploymentStatus as DeploymentStatusEnum
from app.schemas.deployment import (
    DeploymentCreate,
    DeploymentUpdate,
    DeploymentResponse,
    DeploymentListResponse,
)

router = APIRouter(prefix="/deployment", tags=["🚀 Deployment Monitor"])


@router.get("/list", response_model=DeploymentListResponse)
def get_deployments(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
):
    """Get deployment history"""
    deployments = (
        db.query(Deployment)
        .order_by(Deployment.started_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    total = db.query(Deployment).count()
    
    return DeploymentListResponse(
        deployments=deployments,
        total=total,
    )


@router.get("/latest", response_model=DeploymentResponse)
def get_latest_deployment(db: Session = Depends(get_db)):
    """Get the most recent deployment"""
    deployment = (
        db.query(Deployment)
        .order_by(Deployment.started_at.desc())
        .first()
    )
    
    if not deployment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No deployments found",
        )
    
    return deployment


@router.get("/{deployment_id}", response_model=DeploymentResponse)
def get_deployment(
    deployment_id: int,
    db: Session = Depends(get_db),
):
    """Get deployment by ID"""
    deployment = db.query(Deployment).filter(Deployment.id == deployment_id).first()
    
    if not deployment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deployment not found",
        )
    
    return deployment


@router.post("/", response_model=DeploymentResponse)
def create_deployment(
    deployment_in: DeploymentCreate,
    db: Session = Depends(get_db),
):
    """Create a new deployment record"""
    deployment = Deployment(
        version=deployment_in.version,
        git_commit=deployment_in.git_commit,
        deploy_type=deployment_in.deploy_type,
        status=DeploymentStatusEnum.PENDING,
        phase_timings={},
    )
    
    db.add(deployment)
    db.commit()
    db.refresh(deployment)
    
    return deployment


@router.patch("/{deployment_id}", response_model=DeploymentResponse)
def update_deployment(
    deployment_id: int,
    deployment_in: DeploymentUpdate,
    db: Session = Depends(get_db),
):
    """Update deployment status and timings"""
    deployment = db.query(Deployment).filter(Deployment.id == deployment_id).first()
    
    if not deployment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deployment not found",
        )
    
    # Update fields
    if deployment_in.status is not None:
        deployment.status = deployment_in.status
        
        # Auto-set completed_at when status is success or failed
        if deployment_in.status in [DeploymentStatusEnum.SUCCESS, DeploymentStatusEnum.FAILED]:
            deployment.completed_at = datetime.utcnow()
    
    if deployment_in.phase_timings is not None:
        # Merge phase timings
        current_timings = deployment.phase_timings or {}
        current_timings.update(deployment_in.phase_timings)
        deployment.phase_timings = current_timings
    
    if deployment_in.total_time is not None:
        deployment.total_time = deployment_in.total_time
    
    if deployment_in.error_message is not None:
        deployment.error_message = deployment_in.error_message
    
    db.commit()
    db.refresh(deployment)
    
    return deployment


@router.delete("/{deployment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_deployment(
    deployment_id: int,
    db: Session = Depends(get_db),
):
    """Delete a deployment record"""
    deployment = db.query(Deployment).filter(Deployment.id == deployment_id).first()
    
    if not deployment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deployment not found",
        )
    
    db.delete(deployment)
    db.commit()
    
    return None

