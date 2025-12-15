#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API Router for Mẫu 2C-TCTW-98
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from app.services.mau_2c_service import Mau2CService
import os

router = APIRouter(prefix="/api/mau-2c", tags=["Mẫu 2C"])

# Pydantic models
class HocTapItem(BaseModel):
    ten_truong: str
    nganh_hoc: str
    thoi_gian: str
    hinh_thuc: str
    van_bang: str

class CongTacItem(BaseModel):
    thoi_gian: str
    chuc_vu_don_vi: str
    den_thang_nam: Optional[str] = ""

class GiaDinhMember(BaseModel):
    quan_he: str
    ho_ten: str
    nam_sinh: str
    thong_tin: str

class LuongItem(BaseModel):
    thang_nam: str
    ngach_bac: str
    he_so: str

class Mau2CData(BaseModel):
    # Header
    tinh: str
    don_vi_truc_thuoc: str
    don_vi_co_so: str
    so_hieu: str
    
    # Personal info
    ho_ten: str
    gioi_tinh: str
    ten_goi_khac: Optional[str] = ""
    cap_uy_hien_tai: str
    cap_uy_kiem: Optional[str] = "Không"
    chuc_vu_full: str
    phu_cap_chuc_vu: Optional[str] = ""
    
    # Birth info
    ngay: str
    thang: str
    nam: str
    noi_sinh: str
    
    # Origin
    que_quan_xa: str
    que_quan_huyen: str
    que_quan_tinh: str
    
    # Contact
    noi_o_hien_nay: str
    dien_thoai: str
    email: Optional[str] = ""
    
    # Background
    dan_toc: str
    ton_giao: str
    thanh_phan_xuat_than: str
    nghe_nghiep_ban_than: str
    
    # Career dates
    ngay_tuyen_dung: str
    co_quan_tuyen_dung: str
    ngay_vao_co_quan: str
    ngay_tham_gia_cach_mang: Optional[str] = "Không"
    ngay_vao_dang: Optional[str] = ""
    ngay_chinh_thuc_dang: Optional[str] = ""
    ngay_tham_gia_to_chuc: Optional[str] = ""
    ngay_nhap_ngu: Optional[str] = "Không"
    ngay_xuat_ngu: Optional[str] = "Không"
    quan_ham: Optional[str] = "Không"
    
    # Education
    trinh_do_giao_duc_pho_thong: str
    hoc_ham_hoc_vi: str
    ly_luan_chinh_tri: str
    ngoai_ngu: str
    quan_ly_nha_nuoc: Optional[str] = "Chưa có"
    tin_hoc: Optional[str] = ""
    
    # Work
    cong_tac_chinh: Optional[str] = ""
    ngach_cong_chuc: str
    ma_ngach: str
    bac_luong: str
    he_so_luong: str
    tu_thang_nam: str
    
    danh_hieu: Optional[str] = "Không"
    so_truong_cong_tac: Optional[str] = ""
    cong_viec_lau_nhat: Optional[str] = ""
    khen_thuong: Optional[str] = ""
    ky_luat: Optional[str] = "Không"
    
    # Health
    suc_khoe: str
    chieu_cao: str
    can_nang: str
    nhom_mau: str
    
    # ID
    so_cmnd: str
    ngay_cap: Optional[str] = ""
    noi_cap: Optional[str] = ""
    thuong_binh_loai: Optional[str] = "Không"
    gia_dinh_liet_si: Optional[str] = "Không"
    
    # History
    lich_su_bi_bat: Optional[str] = "Không. Chưa từng bị bắt, bị tù."
    lam_viec_che_do_cu: Optional[str] = "Không. Không làm việc trong chế độ cũ."
    quan_he_nuoc_ngoai: Optional[str] = "Không tham gia tổ chức nước ngoài."
    than_nhan_nuoc_ngoai: Optional[str] = "Không có thân nhân ở nước ngoài."
    
    # Arrays
    dao_tao: List[HocTapItem]
    cong_tac: List[CongTacItem]
    gia_dinh: List[GiaDinhMember]
    gia_dinh_vo_chong: List[GiaDinhMember]
    luong: List[LuongItem]

@router.post("/generate")
async def generate_mau_2c(data: Mau2CData):
    """
    Generate Mẫu 2C-TCTW-98 document
    
    Returns path to generated file
    """
    try:
        service = Mau2CService()
        output_path = service.generate(data.dict())
        
        return {
            "success": True,
            "message": "Mẫu 2C generated successfully",
            "file_path": output_path,
            "filename": os.path.basename(output_path)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-and-download")
async def generate_and_download(data: Mau2CData):
    """
    Generate Mẫu 2C and return file for download
    """
    try:
        service = Mau2CService()
        output_path = service.generate(data.dict())
        
        if not os.path.exists(output_path):
            raise HTTPException(status_code=404, detail="Generated file not found")
        
        return FileResponse(
            path=output_path,
            filename=os.path.basename(output_path),
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sample-templates")
async def get_sample_templates():
    """Get list of available sample templates"""
    return {
        "templates": [
            {
                "id": "can_bo_tre",
                "name": "Cán bộ trẻ - Chuyên viên",
                "description": "Nam, 27 tuổi, mới tốt nghiệp ĐH, làm việc 5 năm, chưa lập gia đình"
            },
            {
                "id": "can_bo_chinh",
                "name": "Cán bộ chính - Phó Phòng",
                "description": "Nữ, 38 tuổi, đã có gia đình, 15 năm kinh nghiệm, chức vụ lãnh đạo"
            },
            {
                "id": "can_bo_cao_cap",
                "name": "Cán bộ cao cấp - Trưởng Phòng",
                "description": "Nam, 48 tuổi, Thạc sĩ, 25 năm kinh nghiệm, nhiều khen thưởng"
            }
        ]
    }

@router.get("/sample-data/{template_id}")
async def get_sample_data_by_template(template_id: str):
    """Get sample data by template ID"""
    
    # Template 1: Cán bộ trẻ - Chuyên viên
    if template_id == "can_bo_tre":
        return {
            "tinh": "TP. Hồ Chí Minh",
            "don_vi_truc_thuoc": "UBND Quận 1",
            "don_vi_co_so": "Phòng Tổ chức - Cán bộ",
            "so_hieu": "Q1-TCCB-2024-015",
            "ho_ten": "Trần Minh Tuấn",
            "gioi_tinh": "Nam",
            "ten_goi_khac": "Tuấn",
            "cap_uy_hien_tai": "Đảng viên - Chi bộ Phòng TCCB",
            "cap_uy_kiem": "Không",
            "chuc_vu_full": "Chuyên viên - Phòng Tổ chức Cán bộ UBND Quận 1",
            "phu_cap_chuc_vu": "0.1 (hệ số)",
            "ngay": "15",
            "thang": "03",
            "nam": "1998",
            "noi_sinh": "Phường Bến Nghé, Quận 1, TP.HCM",
            "que_quan_xa": "Xã Tân Thạnh Đông",
            "que_quan_huyen": "Huyện Củ Chi",
            "que_quan_tinh": "TP. Hồ Chí Minh",
            "noi_o_hien_nay": "45/12 Lý Tự Trọng, Phường Bến Nghé, Quận 1, TP.HCM",
            "dien_thoai": "0938.123.456",
            "email": "tranminhtuan@quan1.hochiminhcity.gov.vn",
            "dan_toc": "Kinh",
            "ton_giao": "Không",
            "thanh_phan_xuat_than": "Công nhân",
            "nghe_nghiep_ban_than": "Sinh viên",
            "ngay_tuyen_dung": "01/07/2020",
            "co_quan_tuyen_dung": "UBND Quận 1 TP.HCM",
            "ngay_vao_co_quan": "15/07/2020",
            "ngay_tham_gia_cach_mang": "Không",
            "ngay_vao_dang": "15/06/2022",
            "ngay_chinh_thuc_dang": "15/06/2023",
            "ngay_tham_gia_to_chuc": "Đoàn TNCS HCM: 15/09/2013; Công đoàn: 01/08/2020",
            "ngay_nhap_ngu": "Không",
            "ngay_xuat_ngu": "Không",
            "quan_ham": "Không",
            "trinh_do_giao_duc_pho_thong": "12/12",
            "hoc_ham_hoc_vi": "Cử nhân Hành chính, ĐH Khoa học Xã hội và Nhân văn TP.HCM, 2020, Quản lý hành chính nhà nước",
            "ly_luan_chinh_tri": "Trung cấp LLCT",
            "ngoai_ngu": "Tiếng Anh B1 (TOEIC 600)",
            "quan_ly_nha_nuoc": "Chưa có",
            "tin_hoc": "Tin học văn phòng MOS Excel, Word",
            "cong_tac_chinh": "Quản lý hồ sơ cán bộ, công chức, viên chức",
            "ngach_cong_chuc": "Chuyên viên",
            "ma_ngach": "01.003",
            "bac_luong": "2",
            "he_so_luong": "2.22",
            "tu_thang_nam": "07/2022",
            "danh_hieu": "Không",
            "so_truong_cong_tac": "Quản lý hồ sơ, văn thư lưu trữ",
            "cong_viec_lau_nhat": "Quản lý hồ sơ cán bộ",
            "khen_thuong": "Giấy khen Chủ tịch UBND Quận 1 năm 2023",
            "ky_luat": "Không",
            "suc_khoe": "Tốt",
            "chieu_cao": "1m72",
            "can_nang": "68 kg",
            "nhom_mau": "A",
            "so_cmnd": "001098123456",
            "ngay_cap": "20/03/2016",
            "noi_cap": "CA TP.HCM",
            "thuong_binh_loai": "Không",
            "gia_dinh_liet_si": "Không",
            "lich_su_bi_bat": "Không. Chưa từng bị bắt, bị tù.",
            "lam_viec_che_do_cu": "Không. Không làm việc trong chế độ cũ.",
            "quan_he_nuoc_ngoai": "Không tham gia tổ chức nước ngoài.",
            "than_nhan_nuoc_ngoai": "Không có thân nhân ở nước ngoài.",
            "dao_tao": [
                {
                    "ten_truong": "ĐH Khoa học Xã hội và Nhân văn TP.HCM",
                    "nganh_hoc": "Quản lý hành chính nhà nước",
                    "thoi_gian": "2016-2020",
                    "hinh_thuc": "Chính quy",
                    "van_bang": "Cử nhân Hành chính"
                },
                {
                    "ten_truong": "Trường Chính trị TP.HCM",
                    "nganh_hoc": "Lý luận chính trị",
                    "thoi_gian": "2021-2022",
                    "hinh_thuc": "Bồi dưỡng",
                    "van_bang": "Chứng chỉ Trung cấp LLCT"
                }
            ],
            "cong_tac": [
                {
                    "thoi_gian": "07/2020 - 06/2022",
                    "chuc_vu_don_vi": "Chuyên viên - Phòng TCCB UBND Quận 1\n(Bậc 1, hệ số 2.10)"
                },
                {
                    "thoi_gian": "07/2022 - nay",
                    "chuc_vu_don_vi": "Chuyên viên - Phòng TCCB UBND Quận 1\n(Bậc 2, hệ số 2.22, phụ cấp chức vụ 0.1)"
                }
            ],
            "gia_dinh": [
                {
                    "quan_he": "Bố",
                    "ho_ten": "Trần Văn Hùng",
                    "nam_sinh": "1970",
                    "thong_tin": "Công nhân, đang làm việc tại Công ty TNHH Samsung, Quận 9, TP.HCM"
                },
                {
                    "quan_he": "Mẹ",
                    "ho_ten": "Nguyễn Thị Mai",
                    "nam_sinh": "1972",
                    "thong_tin": "Nội trợ, cư trú tại Quận 1, TP.HCM"
                },
                {
                    "quan_he": "Em gái",
                    "ho_ten": "Trần Thị Minh Anh",
                    "nam_sinh": "2001",
                    "thong_tin": "Sinh viên, Đại học Tôn Đức Thắng TP.HCM"
                }
            ],
            "gia_dinh_vo_chong": [],
            "luong": [
                {
                    "thang_nam": "07/2020",
                    "ngach_bac": "Chuyên viên, Bậc 1",
                    "he_so": "2.10"
                },
                {
                    "thang_nam": "07/2022",
                    "ngach_bac": "Chuyên viên, Bậc 2",
                    "he_so": "2.22"
                }
            ]
        }
    
    # Template 2: Cán bộ chính - Phó Phòng
    elif template_id == "can_bo_chinh":
        return {
            "tinh": "Hà Nội",
            "don_vi_truc_thuoc": "UBND Quận Hoàn Kiếm",
            "don_vi_co_so": "Phòng Tài chính - Kế hoạch",
            "so_hieu": "HK-TCKH-2024-028",
            "ho_ten": "Phạm Thị Thu Hà",
            "gioi_tinh": "Nữ",
            "ten_goi_khac": "Hà",
            "cap_uy_hien_tai": "Chi ủy viên - Chi bộ Phòng TCKH",
            "cap_uy_kiem": "Ủy viên BCH Đảng bộ Quận",
            "chuc_vu_full": "Phó Trưởng phòng - Phòng Tài chính Kế hoạch UBND Quận Hoàn Kiếm",
            "phu_cap_chuc_vu": "0.4 (hệ số)",
            "ngay": "08",
            "thang": "07",
            "nam": "1987",
            "noi_sinh": "Phường Hàng Bông, Quận Hoàn Kiếm, Hà Nội",
            "que_quan_xa": "Xã Đông Xuân",
            "que_quan_huyen": "Quận Hoàn Kiếm",
            "que_quan_tinh": "Hà Nội",
            "noi_o_hien_nay": "Số 25 Hàng Đào, Phường Hàng Đào, Quận Hoàn Kiếm, Hà Nội",
            "dien_thoai": "0912.345.678",
            "email": "phamthiha@hoankiem.hanoi.gov.vn",
            "dan_toc": "Kinh",
            "ton_giao": "Không",
            "thanh_phan_xuat_than": "Cán bộ công nhân viên",
            "nghe_nghiep_ban_than": "Sinh viên",
            "ngay_tuyen_dung": "01/09/2010",
            "co_quan_tuyen_dung": "UBND Quận Hoàn Kiếm",
            "ngay_vao_co_quan": "15/09/2010",
            "ngay_tham_gia_cach_mang": "Không",
            "ngay_vao_dang": "15/05/2012",
            "ngay_chinh_thuc_dang": "15/05/2013",
            "ngay_tham_gia_to_chuc": "Đoàn TNCS HCM: 15/09/2002; Công đoàn: 01/10/2010; Hội LHPN: 01/10/2010",
            "ngay_nhap_ngu": "Không",
            "ngay_xuat_ngu": "Không",
            "quan_ham": "Không",
            "trinh_do_giao_duc_pho_thong": "12/12",
            "hoc_ham_hoc_vi": "Cử nhân Tài chính, Học viện Tài chính, 2010, Tài chính Công",
            "ly_luan_chinh_tri": "Cao đẳng LLCT",
            "ngoai_ngu": "Tiếng Anh B2 (IELTS 6.5)",
            "quan_ly_nha_nuoc": "Chứng chỉ bồi dưỡng QLNN chương trình chuyên viên cao cấp",
            "tin_hoc": "Tin học văn phòng nâng cao, Excel chuyên sâu",
            "cong_tac_chinh": "Quản lý tài chính, ngân sách, kế hoạch đầu tư công",
            "ngach_cong_chuc": "Chuyên viên chính",
            "ma_ngach": "01.002",
            "bac_luong": "4",
            "he_so_luong": "3.00",
            "tu_thang_nam": "01/2023",
            "danh_hieu": "Chiến sĩ thi đua cơ sở năm 2022",
            "so_truong_cong_tac": "Tài chính, ngân sách, kế hoạch",
            "cong_viec_lau_nhat": "Quản lý ngân sách quận",
            "khen_thuong": "Bằng khen Chủ tịch UBND TP Hà Nội (2020, 2023); Giấy khen Chủ tịch UBND Quận (2015, 2017, 2019, 2021, 2024)",
            "ky_luat": "Không",
            "suc_khoe": "Tốt",
            "chieu_cao": "1m62",
            "can_nang": "52 kg",
            "nhom_mau": "B",
            "so_cmnd": "001087654321",
            "ngay_cap": "10/08/2015",
            "noi_cap": "CA Hà Nội",
            "thuong_binh_loai": "Không",
            "gia_dinh_liet_si": "Không",
            "lich_su_bi_bat": "Không. Chưa từng bị bắt, bị tù.",
            "lam_viec_che_do_cu": "Không. Không làm việc trong chế độ cũ.",
            "quan_he_nuoc_ngoai": "Không tham gia tổ chức nước ngoài.",
            "than_nhan_nuoc_ngoai": "Không có thân nhân ở nước ngoài.",
            "dao_tao": [
                {
                    "ten_truong": "Học viện Tài chính",
                    "nganh_hoc": "Tài chính Công",
                    "thoi_gian": "2005-2010",
                    "hinh_thuc": "Chính quy",
                    "van_bang": "Cử nhân Tài chính"
                },
                {
                    "ten_truong": "Trường Chính trị Hà Nội",
                    "nganh_hoc": "Lý luận chính trị",
                    "thoi_gian": "2013-2014",
                    "hinh_thuc": "Bồi dưỡng",
                    "van_bang": "Chứng chỉ Cao đẳng LLCT"
                },
                {
                    "ten_truong": "Học viện Hành chính Quốc gia",
                    "nganh_hoc": "Quản lý nhà nước",
                    "thoi_gian": "2018",
                    "hinh_thuc": "Bồi dưỡng",
                    "van_bang": "Chứng chỉ QLNN chuyên viên cao cấp"
                }
            ],
            "cong_tac": [
                {
                    "thoi_gian": "09/2010 - 08/2013",
                    "chuc_vu_don_vi": "Chuyên viên - Phòng TCKH UBND Quận Hoàn Kiếm\n(Bậc 1-2, hệ số 2.10-2.22)"
                },
                {
                    "thoi_gian": "09/2013 - 08/2018",
                    "chuc_vu_don_vi": "Chuyên viên - Phòng TCKH UBND Quận Hoàn Kiếm\n(Bậc 3-4, hệ số 2.34-2.46)"
                },
                {
                    "thoi_gian": "09/2018 - 12/2022",
                    "chuc_vu_don_vi": "Chuyên viên chính - Phòng TCKH UBND Quận Hoàn Kiếm\n(Bậc 1-2, hệ số 2.62-2.78)"
                },
                {
                    "thoi_gian": "01/2023 - nay",
                    "chuc_vu_don_vi": "Phó Trưởng phòng - Phòng TCKH UBND Quận Hoàn Kiếm\n(Bậc 4, hệ số 3.00, phụ cấp chức vụ 0.4)"
                }
            ],
            "gia_dinh": [
                {
                    "quan_he": "Bố",
                    "ho_ten": "Phạm Văn Thanh",
                    "nam_sinh": "1960",
                    "thong_tin": "Nghỉ hưu, nguyên là công chức Sở Tài chính Hà Nội"
                },
                {
                    "quan_he": "Mẹ",
                    "ho_ten": "Nguyễn Thị Lan",
                    "nam_sinh": "1962",
                    "thong_tin": "Nghỉ hưu, nguyên là giáo viên THCS"
                },
                {
                    "quan_he": "Chồng",
                    "ho_ten": "Nguyễn Đức Anh",
                    "nam_sinh": "1985",
                    "thong_tin": "Kỹ sư, Công ty Điện lực Hà Nội"
                },
                {
                    "quan_he": "Con trai",
                    "ho_ten": "Nguyễn Minh Khang",
                    "nam_sinh": "2015",
                    "thong_tin": "Học sinh lớp 4, Trường Tiểu học Hàng Đào"
                },
                {
                    "quan_he": "Con gái",
                    "ho_ten": "Nguyễn Minh An",
                    "nam_sinh": "2018",
                    "thong_tin": "Học sinh lớp 1, Trường Tiểu học Hàng Đào"
                }
            ],
            "gia_dinh_vo_chong": [
                {
                    "quan_he": "Bố chồng",
                    "ho_ten": "Nguyễn Văn Hải",
                    "nam_sinh": "1958",
                    "thong_tin": "Nghỉ hưu, nguyên Trưởng phòng Sở Xây dựng Hà Nội"
                },
                {
                    "quan_he": "Mẹ chồng",
                    "ho_ten": "Trần Thị Thu",
                    "nam_sinh": "1960",
                    "thong_tin": "Nghỉ hưu, nguyên Dược sĩ Bệnh viện Bạch Mai"
                },
                {
                    "quan_he": "Em chồng",
                    "ho_ten": "Nguyễn Đức Bình",
                    "nam_sinh": "1990",
                    "thong_tin": "Bác sĩ, Bệnh viện Đa khoa Đống Đa"
                }
            ],
            "luong": [
                {
                    "thang_nam": "09/2010",
                    "ngach_bac": "Chuyên viên, Bậc 1",
                    "he_so": "2.10"
                },
                {
                    "thang_nam": "09/2013",
                    "ngach_bac": "Chuyên viên, Bậc 3",
                    "he_so": "2.34"
                },
                {
                    "thang_nam": "09/2018",
                    "ngach_bac": "Chuyên viên chính, Bậc 1",
                    "he_so": "2.62"
                },
                {
                    "thang_nam": "01/2023",
                    "ngach_bac": "Chuyên viên chính, Bậc 4",
                    "he_so": "3.00"
                }
            ]
        }
    
    # Template 3: Cán bộ cao cấp - Trưởng Phòng
    elif template_id == "can_bo_cao_cap":
        return {
            "tinh": "Đà Nẵng",
            "don_vi_truc_thuoc": "UBND Quận Hải Châu",
            "don_vi_co_so": "Phòng Tư pháp",
            "so_hieu": "HC-TP-2024-005",
            "ho_ten": "Lê Văn Minh",
            "gioi_tinh": "Nam",
            "ten_goi_khac": "Minh",
            "cap_uy_hien_tai": "Bí thư Chi bộ Phòng Tư pháp",
            "cap_uy_kiem": "Ủy viên Ban Thường vụ Đảng ủy Quận",
            "chuc_vu_full": "Trưởng phòng - Phòng Tư pháp UBND Quận Hải Châu",
            "phu_cap_chuc_vu": "0.6 (hệ số)",
            "ngay": "20",
            "thang": "05",
            "nam": "1977",
            "noi_sinh": "Phường Hải Châu I, Quận Hải Châu, TP. Đà Nẵng",
            "que_quan_xa": "Xã Hòa Phước",
            "que_quan_huyen": "Huyện Hòa Vang",
            "que_quan_tinh": "Đà Nẵng",
            "noi_o_hien_nay": "Số 123 Lê Duẩn, Phường Hải Châu I, Quận Hải Châu, TP. Đà Nẵng",
            "dien_thoai": "0905.234.567",
            "email": "levanminh@haichau.danang.gov.vn",
            "dan_toc": "Kinh",
            "ton_giao": "Không",
            "thanh_phan_xuat_than": "Cán bộ công nhân viên",
            "nghe_nghiep_ban_than": "Sinh viên",
            "ngay_tuyen_dung": "01/08/2000",
            "co_quan_tuyen_dung": "Sở Tư pháp TP. Đà Nẵng",
            "ngay_vao_co_quan": "15/08/2000",
            "ngay_tham_gia_cach_mang": "Không",
            "ngay_vao_dang": "15/05/2003",
            "ngay_chinh_thuc_dang": "15/05/2004",
            "ngay_tham_gia_to_chuc": "Đoàn TNCS HCM: 15/09/1992; Công đoàn: 01/09/2000",
            "ngay_nhap_ngu": "01/11/1995",
            "ngay_xuat_ngu": "01/11/1997",
            "quan_ham": "Hạ sĩ",
            "trinh_do_giao_duc_pho_thong": "12/12",
            "hoc_ham_hoc_vi": "Thạc sĩ Luật, Trường Đại học Luật Hà Nội, 2010, Luật Hiến pháp và Luật Hành chính",
            "ly_luan_chinh_tri": "Cao đẳng LLCT",
            "ngoai_ngu": "Tiếng Anh C1 (IELTS 7.5); Tiếng Pháp B1",
            "quan_ly_nha_nuoc": "Chứng chỉ bồi dưỡng QLNN chương trình cao cấp",
            "tin_hoc": "Tin học văn phòng chuyên sâu, Quản trị mạng cơ bản",
            "cong_tac_chinh": "Quản lý nhà nước về tư pháp, hộ tịch, chứng thực, lý lịch tư pháp",
            "ngach_cong_chuc": "Chuyên viên cao cấp",
            "ma_ngach": "01.001",
            "bac_luong": "5",
            "he_so_luong": "4.06",
            "tu_thang_nam": "01/2024",
            "danh_hieu": "Chiến sĩ thi đua cấp Bộ năm 2015, 2020; Chiến sĩ thi đua cấp thành phố năm 2018, 2022",
            "so_truong_cong_tac": "Tư pháp, hộ tịch, chứng thực, lý lịch tư pháp",
            "cong_viec_lau_nhat": "Quản lý công tác tư pháp",
            "khen_thuong": "Huân chương Lao động hạng Ba (2020); Bằng khen Thủ tướng Chính phủ (2015, 2022); Bằng khen Chủ tịch UBND TP (2010, 2012, 2017, 2019, 2023); Giấy khen UBND Quận (nhiều lần)",
            "ky_luat": "Không",
            "suc_khoe": "Tốt",
            "chieu_cao": "1m70",
            "can_nang": "70 kg",
            "nhom_mau": "O",
            "so_cmnd": "201234567890",
            "ngay_cap": "15/05/2012",
            "noi_cap": "CA Đà Nẵng",
            "thuong_binh_loai": "Không",
            "gia_dinh_liet_si": "Bố là liệt sĩ - hy sinh trong chiến tranh 1975",
            "lich_su_bi_bat": "Không. Chưa từng bị bắt, bị tù.",
            "lam_viec_che_do_cu": "Không. Không làm việc trong chế độ cũ.",
            "quan_he_nuoc_ngoai": "Không tham gia tổ chức nước ngoài. Đã đi công tác nước ngoài: Pháp (2015), Singapore (2018), Nhật Bản (2022).",
            "than_nhan_nuoc_ngoai": "Không có thân nhân định cư nước ngoài.",
            "dao_tao": [
                {
                    "ten_truong": "Đại học Luật Hà Nội",
                    "nganh_hoc": "Luật",
                    "thoi_gian": "1995-2000",
                    "hinh_thuc": "Chính quy",
                    "van_bang": "Cử nhân Luật"
                },
                {
                    "ten_truong": "Trường Chính trị Đà Nẵng",
                    "nganh_hoc": "Lý luận chính trị",
                    "thoi_gian": "2005-2006",
                    "hinh_thuc": "Bồi dưỡng",
                    "van_bang": "Chứng chỉ Cao đẳng LLCT"
                },
                {
                    "ten_truong": "Đại học Luật Hà Nội (Sau đại học)",
                    "nganh_hoc": "Luật Hiến pháp và Luật Hành chính",
                    "thoi_gian": "2008-2010",
                    "hinh_thuc": "Chính quy",
                    "van_bang": "Thạc sĩ Luật"
                },
                {
                    "ten_truong": "Học viện Hành chính Quốc gia",
                    "nganh_hoc": "Quản lý nhà nước",
                    "thoi_gian": "2016",
                    "hinh_thuc": "Bồi dưỡng",
                    "van_bang": "Chứng chỉ QLNN cao cấp"
                }
            ],
            "cong_tac": [
                {
                    "thoi_gian": "08/2000 - 07/2005",
                    "chuc_vu_don_vi": "Chuyên viên - Phòng Hộ tịch, Chứng thực, Sở Tư pháp TP. Đà Nẵng\n(Bậc 1-4, hệ số 2.10-2.46)"
                },
                {
                    "thoi_gian": "08/2005 - 12/2010",
                    "chuc_vu_don_vi": "Chuyên viên chính - Phòng Hộ tịch, Chứng thực, Sở Tư pháp TP. Đà Nẵng\n(Bậc 1-3, hệ số 2.62-2.94)"
                },
                {
                    "thoi_gian": "01/2011 - 12/2015",
                    "chuc_vu_don_vi": "Phó Trưởng phòng - Phòng Tư pháp UBND Quận Hải Châu\n(Chuyên viên chính Bậc 4, hệ số 3.10, phụ cấp CV 0.4)"
                },
                {
                    "thoi_gian": "01/2016 - 12/2020",
                    "chuc_vu_don_vi": "Phó Trưởng phòng - Phòng Tư pháp UBND Quận Hải Châu\n(Chuyên viên cao cấp Bậc 2, hệ số 3.58, phụ cấp CV 0.4)"
                },
                {
                    "thoi_gian": "01/2021 - nay",
                    "chuc_vu_don_vi": "Trưởng phòng - Phòng Tư pháp UBND Quận Hải Châu\n(Chuyên viên cao cấp Bậc 5, hệ số 4.06, phụ cấp CV 0.6)"
                }
            ],
            "gia_dinh": [
                {
                    "quan_he": "Bố",
                    "ho_ten": "Lê Văn Thành (Liệt sĩ)",
                    "nam_sinh": "1950",
                    "thong_tin": "Hy sinh trong chiến tranh năm 1975, là chiến sĩ Quân đội nhân dân Việt Nam"
                },
                {
                    "quan_he": "Mẹ",
                    "ho_ten": "Trần Thị Hoa",
                    "nam_sinh": "1952",
                    "thong_tin": "Nghỉ hưu, nguyên giáo viên THPT, đang sinh sống tại Đà Nẵng"
                },
                {
                    "quan_he": "Vợ",
                    "ho_ten": "Nguyễn Thị Phương",
                    "nam_sinh": "1980",
                    "thong_tin": "Bác sĩ, Bệnh viện Đa khoa Đà Nẵng"
                },
                {
                    "quan_he": "Con trai",
                    "ho_ten": "Lê Minh Đức",
                    "nam_sinh": "2005",
                    "thong_tin": "Học sinh lớp 12, Trường THPT Chuyên Lê Quý Đôn"
                },
                {
                    "quan_he": "Con gái",
                    "ho_ten": "Lê Minh Châu",
                    "nam_sinh": "2008",
                    "thong_tin": "Học sinh lớp 9, Trường THCS Lê Lợi"
                }
            ],
            "gia_dinh_vo_chong": [
                {
                    "quan_he": "Bố vợ",
                    "ho_ten": "Nguyễn Văn Tâm",
                    "nam_sinh": "1955",
                    "thong_tin": "Nghỉ hưu, nguyên Phó Giám đốc Sở Y tế TP. Đà Nẵng"
                },
                {
                    "quan_he": "Mẹ vợ",
                    "ho_ten": "Lê Thị Hương",
                    "nam_sinh": "1958",
                    "thong_tin": "Nghỉ hưu, nguyên Hiệu trưởng Trường Tiểu học Hải Châu"
                },
                {
                    "quan_he": "Anh vợ",
                    "ho_ten": "Nguyễn Văn Hùng",
                    "nam_sinh": "1978",
                    "thong_tin": "Phó Giám đốc Công ty TNHH Du lịch Đà Nẵng"
                },
                {
                    "quan_he": "Em vợ",
                    "ho_ten": "Nguyễn Thị Lan",
                    "nam_sinh": "1985",
                    "thong_tin": "Giáo viên THPT, Trường THPT Phan Châu Trinh"
                }
            ],
            "luong": [
                {
                    "thang_nam": "08/2000",
                    "ngach_bac": "Chuyên viên, Bậc 1",
                    "he_so": "2.10"
                },
                {
                    "thang_nam": "08/2005",
                    "ngach_bac": "Chuyên viên chính, Bậc 1",
                    "he_so": "2.62"
                },
                {
                    "thang_nam": "01/2011",
                    "ngach_bac": "Chuyên viên chính, Bậc 4",
                    "he_so": "3.10"
                },
                {
                    "thang_nam": "01/2016",
                    "ngach_bac": "Chuyên viên cao cấp, Bậc 2",
                    "he_so": "3.58"
                },
                {
                    "thang_nam": "01/2021",
                    "ngach_bac": "Chuyên viên cao cấp, Bậc 5",
                    "he_so": "4.06"
                }
            ]
        }
    
    else:
        raise HTTPException(status_code=404, detail="Template not found")

@router.get("/sample-data")
async def get_sample_data():
    """
    Return default sample data for testing (backwards compatibility)
    Redirects to can_bo_tre template
    """
    return await get_sample_data_by_template("can_bo_tre")
