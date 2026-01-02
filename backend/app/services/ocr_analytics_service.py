# -*- coding: utf-8 -*-
"""
OCR Analytics Service - Sales Intelligence & User Behavior Tracking
"""
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import json
import logging

from app.models.ocr_analytics import OCRUsageLog, OCRUserAction, OCRConversionFunnel

logger = logging.getLogger(__name__)


class OCRAnalyticsService:
    """
    Service để log và phân tích hành vi người dùng
    → Tối ưu conversion funnel, cải thiện UX, tăng doanh số
    """
    
    @staticmethod
    def log_ocr_usage(
        db: Session,
        user_id: int,
        file_name: str,
        file_size_bytes: int,
        file_type: str,
        total_pages: int = 1,
        detection_method: Optional[str] = None,
        is_scanned: bool = False,
        processing_time_seconds: Optional[float] = None,
        gemini_model_used: Optional[str] = None,
        tokens_used: int = 0,
        cost_usd: float = 0.0,
        success: bool = False,
        error_message: Optional[str] = None,
        error_type: Optional[str] = None,
        downloaded: bool = False,
        download_format: Optional[str] = None
    ) -> OCRUsageLog:
        """
        Log chi tiết mỗi lần xử lý OCR
        → Data cho sales analytics, performance monitoring
        """
        log = OCRUsageLog(
            user_id=user_id,
            file_name=file_name,
            file_size_bytes=file_size_bytes,
            file_type=file_type,
            total_pages=total_pages,
            detection_method=detection_method,
            is_scanned=is_scanned,
            processing_time_seconds=processing_time_seconds,
            gemini_model_used=gemini_model_used,
            tokens_used=tokens_used,
            cost_usd=cost_usd,
            success=success,
            error_message=error_message,
            error_type=error_type,
            downloaded=downloaded,
            download_format=download_format,
            completed_at=datetime.utcnow() if success or error_message else None
        )
        
        db.add(log)
        db.commit()
        db.refresh(log)
        
        logger.info(f"📊 OCR log created: user={user_id}, file={file_name}, success={success}")
        return log
    
    @staticmethod
    def log_user_action(
        db: Session,
        user_id: int,
        session_id: str,
        action_type: str,
        action_metadata: Optional[Dict[str, Any]] = None,
        page_url: Optional[str] = None,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> OCRUserAction:
        """
        Log mọi hành động của user trong OCR workflow
        
        Action Types:
        - page_view: User vào trang OCR
        - file_upload: User chọn file
        - detection_start: Bắt đầu phát hiện loại file
        - processing_start: Bắt đầu OCR
        - download_result: Download file kết quả
        - upgrade_click: Click nút nâng cấp
        - quota_warning_shown: Hiện cảnh báo hết quota
        - error_occurred: Gặp lỗi
        """
        action = OCRUserAction(
            user_id=user_id,
            session_id=session_id,
            action_type=action_type,
            action_metadata=json.dumps(action_metadata) if action_metadata else None,
            page_url=page_url,
            user_agent=user_agent,
            ip_address=ip_address
        )
        
        db.add(action)
        db.commit()
        db.refresh(action)
        
        logger.info(f"👤 User action logged: {action_type} by user {user_id}")
        return action
    
    @staticmethod
    def update_conversion_funnel(db: Session, date: Optional[datetime] = None):
        """
        Cập nhật metrics conversion funnel cho sales dashboard
        Auto-aggregates từ OCRUserAction và OCRUsageLog
        """
        if not date:
            date = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Count các stage trong funnel
        page_views = db.query(OCRUserAction).filter(
            OCRUserAction.action_type == "page_view",
            OCRUserAction.created_at >= date,
            OCRUserAction.created_at < date + timedelta(days=1)
        ).count()
        
        file_uploads = db.query(OCRUserAction).filter(
            OCRUserAction.action_type == "file_upload",
            OCRUserAction.created_at >= date,
            OCRUserAction.created_at < date + timedelta(days=1)
        ).count()
        
        processing_started = db.query(OCRUserAction).filter(
            OCRUserAction.action_type == "processing_start",
            OCRUserAction.created_at >= date,
            OCRUserAction.created_at < date + timedelta(days=1)
        ).count()
        
        processing_success = db.query(OCRUsageLog).filter(
            OCRUsageLog.success == True,
            OCRUsageLog.created_at >= date,
            OCRUsageLog.created_at < date + timedelta(days=1)
        ).count()
        
        downloads = db.query(OCRUsageLog).filter(
            OCRUsageLog.downloaded == True,
            OCRUsageLog.created_at >= date,
            OCRUsageLog.created_at < date + timedelta(days=1)
        ).count()
        
        upgrade_clicks = db.query(OCRUserAction).filter(
            OCRUserAction.action_type == "upgrade_click",
            OCRUserAction.created_at >= date,
            OCRUserAction.created_at < date + timedelta(days=1)
        ).count()
        
        quota_exceeded = db.query(OCRUsageLog).filter(
            OCRUsageLog.error_type == "quota_exceeded",
            OCRUsageLog.created_at >= date,
            OCRUsageLog.created_at < date + timedelta(days=1)
        ).count()
        
        # Calculate conversion rates
        upload_rate = (file_uploads / page_views * 100) if page_views > 0 else 0.0
        success_rate = (processing_success / processing_started * 100) if processing_started > 0 else 0.0
        download_rate = (downloads / processing_success * 100) if processing_success > 0 else 0.0
        upgrade_rate = (upgrade_clicks / quota_exceeded * 100) if quota_exceeded > 0 else 0.0
        
        # Find or create funnel record
        funnel = db.query(OCRConversionFunnel).filter(
            OCRConversionFunnel.date == date
        ).first()
        
        if not funnel:
            funnel = OCRConversionFunnel(date=date)
        
        funnel.total_page_views = page_views
        funnel.total_file_uploads = file_uploads
        funnel.total_processing_started = processing_started
        funnel.total_processing_success = processing_success
        funnel.total_downloads = downloads
        funnel.total_upgrade_clicks = upgrade_clicks
        funnel.total_quota_exceeded = quota_exceeded
        funnel.upload_rate = upload_rate
        funnel.success_rate = success_rate
        funnel.download_rate = download_rate
        funnel.upgrade_rate = upgrade_rate
        funnel.updated_at = datetime.utcnow()
        
        db.add(funnel)
        db.commit()
        db.refresh(funnel)
        
        logger.info(f"📈 Conversion funnel updated for {date.date()}")
        return funnel
    
    @staticmethod
    def get_user_ocr_history(
        db: Session,
        user_id: int,
        limit: int = 10,
        offset: int = 0
    ) -> List[OCRUsageLog]:
        """Lấy lịch sử OCR của user"""
        return db.query(OCRUsageLog).filter(
            OCRUsageLog.user_id == user_id
        ).order_by(OCRUsageLog.created_at.desc()).limit(limit).offset(offset).all()
    
    @staticmethod
    def get_ocr_stats(db: Session, user_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Thống kê OCR usage (cho user hoặc toàn hệ thống)
        → Sales insights, usage patterns
        """
        query = db.query(OCRUsageLog)
        if user_id:
            query = query.filter(OCRUsageLog.user_id == user_id)
        
        total_requests = query.count()
        successful = query.filter(OCRUsageLog.success == True).count()
        failed = query.filter(OCRUsageLog.success == False).count()
        
        # File type distribution
        pdf_count = query.filter(OCRUsageLog.file_type.like('%pdf%')).count()
        image_count = query.filter(OCRUsageLog.file_type.like('%image%')).count()
        
        # Detection method distribution
        scanned_count = query.filter(OCRUsageLog.is_scanned == True).count()
        text_based_count = query.filter(OCRUsageLog.is_scanned == False).count()
        
        # Average processing time
        avg_time = query.filter(
            OCRUsageLog.processing_time_seconds != None
        ).with_entities(
            db.func.avg(OCRUsageLog.processing_time_seconds)
        ).scalar() or 0.0
        
        # Total cost
        total_cost = query.with_entities(
            db.func.sum(OCRUsageLog.cost_usd)
        ).scalar() or 0.0
        
        return {
            "total_requests": total_requests,
            "successful": successful,
            "failed": failed,
            "success_rate": (successful / total_requests * 100) if total_requests > 0 else 0.0,
            "file_types": {
                "pdf": pdf_count,
                "image": image_count
            },
            "detection": {
                "scanned": scanned_count,
                "text_based": text_based_count
            },
            "avg_processing_time_seconds": round(avg_time, 2),
            "total_cost_usd": round(total_cost, 4)
        }
