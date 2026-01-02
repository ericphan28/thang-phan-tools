"""
Pydantic schemas cho API Văn bản hành chính
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ViPhamTheThu(BaseModel):
    """Chi tiết 1 vi phạm thể thức"""
    thanh_phan: str = Field(..., description="Thành phần thể thức bị vi phạm")
    mo_ta: str = Field(..., description="Mô tả lỗi chi tiết")
    muc_do: str = Field(..., description="Mức độ nghiêm trọng: CAO/TRUNG_BINH/THAP")
    goi_y_sua: Optional[str] = Field(None, description="Gợi ý cách sửa")


class CheckTheThuResponse(BaseModel):
    """Response sau khi kiểm tra thể thức"""
    success: bool = True
    van_ban_id: Optional[int] = None
    tong_diem: int = Field(..., ge=0, le=100, description="Điểm tổng thể 0-100")
    loai_van_ban: str = Field(..., description="Loại văn bản: CONG_VAN, QUYET_DINH...")
    vi_pham: List[ViPhamTheThu] = Field(default_factory=list)
    dat_yeu_cau: List[str] = Field(default_factory=list, description="Các thành phần đạt yêu cầu")
    message: Optional[str] = None


class CheckTheThuRequest(BaseModel):
    """Request kiểm tra thể thức (nếu cần thêm params)"""
    luu_database: bool = Field(True, description="Có lưu kết quả vào DB không")
    chi_tiet_cao: bool = Field(False, description="Kiểm tra chi tiết cao (mất nhiều token hơn)")


class VanBanHanhChinhBase(BaseModel):
    """Base schema cho văn bản"""
    loai_van_ban: Optional[str] = None
    so_ky_hieu: Optional[str] = None
    trich_yeu: Optional[str] = None
    muc_do_khan: Optional[str] = None
    don_vi_xu_ly: Optional[str] = None


class VanBanHanhChinhResponse(VanBanHanhChinhBase):
    """Response chi tiết văn bản"""
    id: int
    user_id: int
    file_name: Optional[str] = None
    diem_the_thuc: Optional[int] = None
    trang_thai: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class VanBanListResponse(BaseModel):
    """Response danh sách văn bản"""
    total: int
    items: List[VanBanHanhChinhResponse]
    page: int = 1
    page_size: int = 20
