"""
Models cho quản lý văn bản hành chính
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.core.database import Base


class MucDoKhan(enum.Enum):
    """Mức độ khẩn của văn bản theo NĐ 30/2020"""
    HOA_TOC = "Hỏa tốc"
    THUONG_KHAN = "Thượng khẩn"
    KHAN = "Khẩn"
    BINH_THUONG = "Bình thường"


class TrangThaiVanBan(enum.Enum):
    """Trạng thái xử lý văn bản"""
    CHO_XU_LY = "Chờ xử lý"
    DANG_XU_LY = "Đang xử lý"
    HOAN_THANH = "Hoàn thành"
    QUA_HAN = "Quá hạn"


class VanBanHanhChinh(Base):
    """
    Bảng lưu thông tin văn bản hành chính đã xử lý
    """
    __tablename__ = "van_ban_hanh_chinh"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Thông tin file
    file_url = Column(String(500))
    file_name = Column(String(255))
    file_type = Column(String(50))  # PDF, DOCX, IMAGE
    
    # Thông tin văn bản
    loai_van_ban = Column(String(50))  # CONG_VAN, QUYET_DINH, BAO_CAO...
    so_ky_hieu = Column(String(100))
    ngay_ban_hanh = Column(DateTime)
    trich_yeu = Column(Text)
    noi_dung_full = Column(Text)  # Full OCR content
    
    # Phân loại
    muc_do_khan = Column(Enum(MucDoKhan), default=MucDoKhan.BINH_THUONG)
    do_uu_tien = Column(Integer, default=3)  # 1=Cao, 2=TB, 3=Thấp
    don_vi_xu_ly = Column(String(200))  # Phòng/Ban xử lý
    han_xu_ly = Column(DateTime)
    trang_thai = Column(Enum(TrangThaiVanBan), default=TrangThaiVanBan.CHO_XU_LY)
    
    # Kết quả kiểm tra thể thức
    diem_the_thuc = Column(Integer)  # 0-100
    vi_pham_the_thuc = Column(JSON)  # [{"thanh_phan": "...", "mo_ta": "..."}]
    dat_yeu_cau = Column(JSON)  # ["quoc_hieu", "tieu_ngu", ...]
    tom_tat_lanh_dao = Column(Text)  # Tóm tắt cho lãnh đạo
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships (one-way only, không cần back_populates)
    user = relationship("User")


# Không cần thêm relationship vào User model
# Vì không bắt buộc phải có relationship 2 chiều
