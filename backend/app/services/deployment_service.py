"""Deployment tracking service"""
import json
from pathlib import Path
from typing import List, Optional
from datetime import datetime
from ..schemas.deployment import DeploymentLog, DeploymentStatus, DeploymentPhase


class DeploymentService:
    """Service for tracking deployment history"""
    
    def __init__(self, log_file: str = "deployment_history.json"):
        self.log_file = Path(log_file)
        self._ensure_log_file()
    
    def _ensure_log_file(self):
        """Create log file if it doesn't exist"""
        if not self.log_file.exists():
            self.log_file.write_text("[]")
    
    def _read_logs(self) -> List[dict]:
        """Read deployment logs from file"""
        try:
            return json.loads(self.log_file.read_text())
        except Exception:
            return []
    
    def _write_logs(self, logs: List[dict]):
        """Write deployment logs to file"""
        self.log_file.write_text(json.dumps(logs, indent=2, default=str))
    
    def add_deployment(self, deployment: DeploymentLog):
        """Add a new deployment log entry"""
        logs = self._read_logs()
        logs.insert(0, deployment.model_dump(mode='json'))  # Most recent first
        # Keep last 100 deployments
        logs = logs[:100]
        self._write_logs(logs)
    
    def get_history(self, limit: int = 20) -> List[DeploymentLog]:
        """Get deployment history"""
        logs = self._read_logs()
        return [DeploymentLog(**log) for log in logs[:limit]]
    
    def get_latest(self) -> Optional[DeploymentLog]:
        """Get the latest deployment"""
        logs = self._read_logs()
        if logs:
            return DeploymentLog(**logs[0])
        return None
    
    def get_current_status(self, current_version: str) -> DeploymentStatus:
        """Get current deployment status"""
        latest = self.get_latest()
        
        # Check if there's an in-progress deployment
        is_deploying = False
        if latest and latest.status == "in-progress":
            is_deploying = True
        
        deployed_at = None
        if latest and latest.status == "completed":
            deployed_at = latest.timestamp
        
        return DeploymentStatus(
            current_version=current_version,
            deployed_at=deployed_at,
            latest_deploy=latest,
            is_deploying=is_deploying
        )


# Singleton instance
deployment_service = DeploymentService()
