"""
Script phân tích CHI TIẾT những gì còn thiếu và tạo JSON HOÀN CHỈNH
"""

from docx import Document
import json
from pathlib import Path

def analyze_tables_detailed():
    """
    Phân tích CHI TIẾT 5 bảng trong OUTPUT
    """
    print("="*80)
    print("📊 PHÂN TÍCH CHI TIẾT 5 BẢNG")
    print("="*80)
    
    doc = Document("OUTPUT_MAU_2C_DOCXTPL.docx")
    
    for table_idx, table in enumerate(doc.tables):
        print(f"\n{'='*80}")
        print(f"📋 BẢNG {table_idx + 1}: {len(table.rows)} rows × {len(table.columns)} cols")
        print("="*80)
        
        for row_idx, row in enumerate(table.rows):
            print(f"\n📌 Row {row_idx + 1}:")
            for col_idx, cell in enumerate(row.cells):
                text = cell.text.strip()[:100]
                print(f"   Col {col_idx + 1}: {text}")

def create_complete_json():
    """
    Tạo JSON HOÀN CHỈNH với TẤT CẢ dữ liệu cần thiết
    """
    
    complete_data = {
        "_comment": "JSON HOÀN CHỈNH 100% - Mẫu 2C-TCTW-98",
        "_version": "3.1 - COMPLETE",
        "_date": "2024-11-26",
        
        # ========== HEADER ==========
        "_section_header": "=== HEADER ===",
        "tinh": "Bình Dương",
        "don_vi_truc_thuoc": "UBND Thành phố Thủ Dầu Một",
        "don_vi_co_so": "Phòng Nội vụ",
        "so_hieu": "BD-NV-2024-001",
        
        # ========== MỤC 1-3: HỌ TÊN, CHỨC VỤ ==========
        "_section_1_3": "=== MỤC 1-3 ===",
        "ho_ten": "Nguyễn Văn An",
        "gioi_tinh": "Nam",
        "ten_goi_khac": "An",
        
        "cap_uy_hien_tai": "Chi bộ Phòng Nội vụ",
        "cap_uy_kiem": "Không",
        "chuc_vu_full": "Chuyên viên - Phòng Nội vụ UBND TP Thủ Dầu Một",
        "phu_cap_chuc_vu": "0.2 (hệ số)",
        
        # ========== MỤC 4-7: NGÀY SINH, ĐỊA CHỈ ==========
        "_section_4_7": "=== MỤC 4-7 ===",
        "ngay": "15",
        "thang": "08",
        "nam": "1997",
        "noi_sinh": "Phường Phú Hòa, TP Thủ Dầu Một, Bình Dương",
        
        "que_quan_xa": "Xã Bình An",
        "que_quan_huyen": "Huyện Dĩ An",
        "que_quan_tinh": "Bình Dương",
        
        "noi_o_hien_nay": "123/45 Đại lộ Bình Dương, Phường Phú Lợi, TP Thủ Dầu Một, Bình Dương",
        "dien_thoai": "0909.123.456",
        "email": "nguyenvanan@thuadaumont.gov.vn",
        
        # ========== MỤC 8-11: DÂN TỘC ==========
        "_section_8_11": "=== MỤC 8-11 ===",
        "dan_toc": "Kinh",
        "ton_giao": "Phật giáo",
        "thanh_phan_xuat_than": "Nông dân",
        "nghe_nghiep_ban_than": "Sinh viên",
        
        # ========== MỤC 12-16: TUYỂN DỤNG, ĐẢNG ==========
        "_section_12_16": "=== MỤC 12-16 ===",
        "ngay_tuyen_dung": "01/09/2019",
        "co_quan_tuyen_dung": "UBND TP Thủ Dầu Một",
        "ngay_vao_co_quan": "15/09/2019",
        "ngay_tham_gia_cach_mang": "Không",
        
        "ngay_vao_dang": "15/05/2022",
        "ngay_chinh_thuc_dang": "15/05/2023",
        "ngay_tham_gia_to_chuc": "Đoàn TNCS HCM: 15/09/2012; Công đoàn: 01/10/2019",
        
        "ngay_nhap_ngu": "Không",
        "ngay_xuat_ngu": "Không",
        "quan_ham": "Không",
        
        # ========== MỤC 17: HỌC VẤN ==========
        "_section_17": "=== MỤC 17 ===",
        "trinh_do_giao_duc_pho_thong": "12/12",
        "hoc_ham_hoc_vi": "Cử nhân Luật, Đại học Luật TP.HCM, 2019, Luật Kinh tế",
        "ly_luan_chinh_tri": "Trung cấp LLCT",
        "ngoai_ngu": "Tiếng Anh B1 (TOEIC 550)",
        "quan_ly_nha_nuoc": "Chưa có",
        "tin_hoc": "Tin học văn phòng (MOS)",
        
        # ========== MỤC 18-21: CÔNG TÁC ==========
        "_section_18_21": "=== MỤC 18-21 ===",
        "cong_tac_chinh": "Thẩm định hồ sơ tuyển dụng công chức, viên chức",
        "ngach_cong_chuc": "Chuyên viên",
        "ma_ngach": "01.003",
        "bac_luong": "3",
        "he_so_luong": "2.34",
        "tu_thang_nam": "10/2022",
        
        "danh_hieu": "Không",
        "so_truong_cong_tac": "Văn phòng, soạn thảo văn bản",
        "cong_viec_lau_nhat": "Thẩm định hồ sơ",
        
        # ========== MỤC 22-25: KHEN THƯỞNG ==========
        "_section_22_25": "=== MỤC 22-25 ===",
        "khen_thuong": "Giấy khen Giám đốc Sở Nội vụ 2022",
        "ky_luat": "Không",
        "suc_khoe": "Tốt",
        "chieu_cao": "1m68",
        "can_nang": "62 kg",
        "nhom_mau": "O",
        
        "so_cmnd": "274123456789",
        "ngay_cap": "15/01/2015",
        "noi_cap": "CA Bình Dương",
        "thuong_binh_loai": "Không",
        "gia_dinh_liet_si": "Không",
        
        # ========== GIA ĐÌNH VỢ/CHỒNG ==========
        "_section_gia_dinh": "=== GIA ĐÌNH ===",
        "tinh_trang_hon_nhan": "Đã kết hôn",
        "ten_vo_chong": "Lê Thị Diệu",
        "nam_sinh_vo_chong": "1998",
        "que_quan_vo_chong": "Thủ Dầu Một, Bình Dương",
        "nghe_nghiep_vo_chong": "Giáo viên mầm non",
        "cho_o_vo_chong": "123/45 Đại lộ Bình Dương, Thủ Dầu Một",
        
        # ========== LỊCH SỬ ==========
        "_section_lich_su": "=== LỊCH SỬ ===",
        "lich_su_bi_bat": "Không. Chưa từng bị bắt, bị tù.",
        "lam_viec_che_do_cu": "Không. Không làm việc trong chế độ cũ.",
        "quan_he_nuoc_ngoai": "Không tham gia tổ chức nước ngoài.",
        "than_nhan_nuoc_ngoai": "Không có thân nhân ở nước ngoài.",
        
        # ========== KINH TẾ ==========
        "_section_kinh_te": "=== KINH TẾ ===",
        "nguon_thu_luong": "8.500.000 đ/tháng",
        "nguon_thu_khac": "Không",
        
        "nha_o_duoc_cap": "Không",
        "nha_o_duoc_cap_loai": "Không",
        "nha_o_duoc_cap_dien_tich": "0 m²",
        
        "nha_o_tu_mua": "Có",
        "nha_o_tu_mua_loai": "Căn hộ chung cư Becamex",
        "nha_o_tu_mua_dien_tich": "65 m²",
        
        "dat_o_duoc_cap": "0 m²",
        "dat_o_tu_mua": "0 m²",
        "dat_san_xuat": "Không có",
        
        # ========== CHỮ KÝ ==========
        "_section_ky": "=== CHỮ KÝ ===",
        "ngay_ky": "20",
        "thang_ky": "11",
        "nam_ky": "2024",
        
        # ========== BẢNG 1: ĐÀO TẠO ==========
        "_table_1": "=== BẢNG 1: ĐÀO TẠO ===",
        "dao_tao": [
            {
                "ten_truong": "Đại học Luật TP.HCM",
                "nganh_hoc": "Luật Kinh tế",
                "thoi_gian": "2015-2019",
                "hinh_thuc": "Chính quy",
                "van_bang": "Cử nhân Luật"
            },
            {
                "ten_truong": "Trường Chính trị Bình Dương",
                "nganh_hoc": "Lý luận chính trị",
                "thoi_gian": "2020-2021",
                "hinh_thuc": "Bồi dưỡng",
                "van_bang": "Chứng chỉ Trung cấp LLCT"
            },
            {
                "ten_truong": "Trung tâm Tin học UBND Bình Dương",
                "nganh_hoc": "Tin học văn phòng",
                "thoi_gian": "2019",
                "hinh_thuc": "Bồi dưỡng",
                "van_bang": "Chứng chỉ MOS"
            }
        ],
        
        # ========== BẢNG 2: CÔNG TÁC ==========
        "_table_2": "=== BẢNG 2: CÔNG TÁC ===",
        "cong_tac": [
            {
                "thoi_gian": "09/2019 - 12/2021",
                "chuc_vu_don_vi": "Chuyên viên - Phòng Nội vụ UBND TP Thủ Dầu Một\n(Bậc 1, hệ số 2.10)"
            },
            {
                "thoi_gian": "01/2022 - nay",
                "chuc_vu_don_vi": "Chuyên viên - Phòng Nội vụ UBND TP Thủ Dầu Một\n(Bậc 3, hệ số 2.34, phụ cấp chức vụ 0.2)"
            }
        ],
        
        # ========== BẢNG 3: GIA ĐÌNH BẢN THÂN ==========
        "_table_3": "=== BẢNG 3: GIA ĐÌNH BẢN THÂN ===",
        "gia_dinh": [
            {
                "quan_he": "Bố",
                "ho_ten": "Nguyễn Văn Bình",
                "nam_sinh": "1970",
                "thong_tin": "Nông dân, xã Bình An, Dĩ An, Bình Dương. Đang canh tác tại quê."
            },
            {
                "quan_he": "Mẹ",
                "ho_ten": "Trần Thị Cúc",
                "nam_sinh": "1972",
                "thong_tin": "Nội trợ, xã Bình An, Dĩ An, Bình Dương. Ở quê nhà."
            },
            {
                "quan_he": "Vợ",
                "ho_ten": "Lê Thị Diệu",
                "nam_sinh": "1998",
                "thong_tin": "Giáo viên mầm non, Trường MN Hoa Mai, Thủ Dầu Một. Đang công tác."
            },
            {
                "quan_he": "Em ruột",
                "ho_ten": "Nguyễn Văn Bảo",
                "nam_sinh": "2000",
                "thong_tin": "Công nhân, Công ty Samsung Việt Nam, KCN Vsip. Đang làm việc."
            }
        ],
        
        # ========== BẢNG 4: GIA ĐÌNH VỢ/CHỒNG ==========
        "_table_4": "=== BẢNG 4: GIA ĐÌNH VỢ/CHỒNG ===",
        "gia_dinh_vo_chong": [
            {
                "quan_he": "Bố vợ",
                "ho_ten": "Lê Văn Phúc",
                "nam_sinh": "1968",
                "thong_tin": "Thợ hàn tự do, Thủ Dầu Một. Đang sinh sống tại TP."
            },
            {
                "quan_he": "Mẹ vợ",
                "ho_ten": "Trần Thị Giang",
                "nam_sinh": "1970",
                "thong_tin": "Buôn bán chợ Bình Dương. Kinh doanh nhỏ."
            },
            {
                "quan_he": "Em vợ",
                "ho_ten": "Lê Thị Hoa",
                "nam_sinh": "2002",
                "thong_tin": "Sinh viên, Đại học Kinh tế TP.HCM. Đang học năm 3."
            }
        ],
        
        # ========== BẢNG 5: LƯƠNG ==========
        "_table_5": "=== BẢNG 5: LƯƠNG ===",
        "luong": [
            {
                "thang_nam": "10/2019",
                "ngach_bac": "Chuyên viên, Bậc 1",
                "he_so": "2.10"
            },
            {
                "thang_nam": "10/2021",
                "ngach_bac": "Chuyên viên, Bậc 2",
                "he_so": "2.22"
            },
            {
                "thang_nam": "10/2022",
                "ngach_bac": "Chuyên viên, Bậc 3",
                "he_so": "2.34"
            }
        ]
    }
    
    # Save JSON
    output_path = Path("mau_2c_DATA_COMPLETE_V3.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(complete_data, f, ensure_ascii=False, indent=2)
    
    file_size = output_path.stat().st_size
    
    print("\n" + "="*80)
    print("✅ ĐÃ TẠO JSON HOÀN CHỈNH!")
    print("="*80)
    print(f"📄 File: {output_path}")
    print(f"📊 Size: {file_size:,} bytes ({file_size/1024:.2f} KB)")
    
    # Count fields
    simple_fields = sum(1 for k, v in complete_data.items() 
                       if not k.startswith('_') and not isinstance(v, list))
    array_fields = sum(1 for k, v in complete_data.items() 
                      if not k.startswith('_') and isinstance(v, list))
    
    # Count array items
    total_array_items = 0
    for k, v in complete_data.items():
        if not k.startswith('_') and isinstance(v, list):
            total_array_items += len(v)
            print(f"   - {k}: {len(v)} items")
    
    print(f"\n💡 Tổng cộng:")
    print(f"   - Simple fields: {simple_fields}")
    print(f"   - Array fields: {array_fields}")
    print(f"   - Total array items: {total_array_items}")
    print(f"   - TOTAL: {simple_fields + array_fields} fields")
    
    return complete_data

if __name__ == "__main__":
    print("🚀 TẠO JSON HOÀN CHỈNH 100%")
    print("="*80)
    
    # Analyze tables first
    analyze_tables_detailed()
    
    # Create complete JSON
    print("\n\n")
    create_complete_json()
    
    print("\n✅ HOÀN TẤT!")
    print("🎯 Test ngay: python test_docxtpl.py")
