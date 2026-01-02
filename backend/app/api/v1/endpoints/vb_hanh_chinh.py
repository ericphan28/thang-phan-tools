"""
API endpoints cho Văn bản hành chính
"""
import os
import tempfile
import logging
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from typing import Optional

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models.auth_models import User
from app.services.vb_checker_service import VBCheckerService
from app.schemas.van_ban_schemas import CheckTheThuResponse

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/check-the-thuc", response_model=CheckTheThuResponse)
async def check_the_thuc_van_ban(
    file: UploadFile = File(..., description="File văn bản (PDF, DOCX, hoặc ảnh)"),
    chi_tiet_cao: bool = Form(False, description="Kiểm tra chi tiết (tốn nhiều token hơn)"),
    luu_database: bool = Form(True, description="Lưu kết quả vào database"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Kiểm tra thể thức văn bản hành chính theo Nghị định 30/2020/NĐ-CP
    
    **Các loại văn bản được hỗ trợ:**
    - PDF (scan hoặc digital)
    - DOCX/DOC (Microsoft Word)
    - JPG/PNG (ảnh scan văn bản)
    
    **Các thành phần được kiểm tra:**
    1. Quốc hiệu và Tiêu ngữ
    2. Tên cơ quan ban hành
    3. Số ký hiệu văn bản
    4. Ngày tháng ban hành
    5. Trích yếu nội dung
    6. Nội dung văn bản (cấu trúc)
    7. Chức vụ và người ký
    8. Nơi nhận
    9. Font chữ và trình bày
    10. Các thành phần bổ sung
    
    **Response:**
    - `tong_diem`: Điểm tổng thể 0-100
    - `vi_pham`: Danh sách lỗi vi phạm thể thức
    - `dat_yeu_cau`: Các thành phần đạt yêu cầu
    - `loai_van_ban`: Loại văn bản được nhận diện
    """
    temp_path = None
    
    try:
        # Validate file extension
        allowed_extensions = ['.pdf', '.docx', '.doc', '.jpg', '.jpeg', '.png', '.txt']
        file_ext = os.path.splitext(file.filename)[1].lower()
        
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Định dạng file không được hỗ trợ. Chỉ chấp nhận: {', '.join(allowed_extensions)}"
            )
        
        # Validate file size (max 10MB)
        file_content = await file.read()
        file_size_mb = len(file_content) / (1024 * 1024)
        
        if file_size_mb > 10:
            raise HTTPException(
                status_code=400,
                detail=f"File quá lớn ({file_size_mb:.1f}MB). Giới hạn 10MB."
            )
        
        # Save temp file (Windows-compatible)
        temp_dir = Path(tempfile.gettempdir())
        temp_file_name = f"vb_{current_user.id}_{file.filename}"
        temp_path = temp_dir / temp_file_name
        
        with open(temp_path, "wb") as f:
            f.write(file_content)
        
        logger.info(f"User {current_user.username} checking document: {file.filename}")
        
        # Check thể thức
        checker = VBCheckerService(db, current_user.id)
        result = await checker.check_the_thuc(
            file_path=str(temp_path),
            file_name=file.filename,
            chi_tiet_cao=chi_tiet_cao,
            luu_database=luu_database
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result.get("message", "Lỗi không xác định"))
        
        return CheckTheThuResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in check_the_thuc endpoint: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi khi xử lý văn bản: {str(e)}"
        )
    finally:
        # Cleanup temp file
        if temp_path and temp_path.exists():
            try:
                temp_path.unlink()
            except Exception as e:
                logger.warning(f"Could not delete temp file {temp_path}: {str(e)}")


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "service": "van-ban-hanh-chinh"}
