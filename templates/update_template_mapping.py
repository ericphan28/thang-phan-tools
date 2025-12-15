"""
Script cập nhật template với MAPPING CHÍNH XÁC cho 60+ fields
"""

from docx import Document
import re
from pathlib import Path

def update_template_with_correct_mapping():
    """
    Cập nhật template với mapping chính xác từ phân tích missing data
    """
    
    print("🔧 CẬP NHẬT TEMPLATE VỚI MAPPING CHÍNH XÁC")
    print("="*80)
    
    # Load template
    template_path = Path("mau_2c_template_docxtpl.docx")
    if not template_path.exists():
        print(f"❌ Không tìm thấy {template_path}")
        return False
    
    doc = Document(template_path)
    
    # ENHANCED MAPPING - từ phân tích missing data
    replacements = [
        # Header
        (r"Đơn vị trực thuộc:\s*\.{3,}", "Đơn vị trực thuộc: {{ don_vi_truc_thuoc }}"),
        (r"Đơn vị cơ sở:\s*\.{3,}", "Đơn vị cơ sở: {{ don_vi_co_so }}"),
        (r"Số hiệu.*?:\s*\.{3,}", "Số hiệu: {{ so_hieu }}"),
        
        # Mục 1-3
        (r"Nam, nữ:\s*\.{3,}", "Nam, nữ: {{ gioi_tinh }}"),
        (r"Các tên gọi khác:\s*\.{3,}", "Các tên gọi khác: {{ ten_goi_khac }}"),
        (r"Cấp ủy hiện tại:\s*\.{3,}", "Cấp ủy hiện tại: {{ cap_uy_hien_tai }}"),
        (r"Cấp ủy kiêm:\s*\.{3,}", "Cấp ủy kiêm: {{ cap_uy_kiem }}"),
        (r"Chức vụ.*?:\s*\.{3,}", "Chức vụ: {{ chuc_vu_full }}"),
        (r"Phụ cấp chức vụ:\s*\.{3,}", "Phụ cấp chức vụ: {{ phu_cap_chuc_vu }}"),
        
        # Mục 4-7: Địa chỉ
        (r"Nơi sinh:\s*\.{3,}", "Nơi sinh: {{ noi_sinh }}"),
        (r"\(xã, phường\):\s*\.{3,}", "(xã, phường): {{ que_quan_xa }}"),
        (r"\(huyện, quận\):\s*\.{3,}", "(huyện, quận): {{ que_quan_huyen }}"),
        (r"\(tỉnh, TP\):\s*\.{3,}", "(tỉnh, TP): {{ que_quan_tinh }}"),
        (r"Nơi ở hiện nay.*?:\s*\.{3,}", "Nơi ở hiện nay: {{ noi_o_hien_nay }}"),
        (r"đ/thoại:\s*\.{3,}", "đ/thoại: {{ dien_thoai }}"),
        
        # Mục 8-11
        (r"Dân tộc:.*?:\s*\.{3,}", "Dân tộc: {{ dan_toc }}"),
        (r"Tôn giáo:\s*\.{3,}", "Tôn giáo: {{ ton_giao }}"),
        (r"Thành phần gia đình xuất thân:\s*\.{3,}", "Thành phần gia đình xuất thân: {{ thanh_phan_xuat_than }}"),
        (r"Nghề nghiệp bản thân.*?:\s*\.{3,}", "Nghề nghiệp bản thân: {{ nghe_nghiep_ban_than }}"),
        
        # Mục 12-13
        (r"Ngày được tuyển dụng:\s*\.{3,}", "Ngày được tuyển dụng: {{ ngay_tuyen_dung }}"),
        (r"Vào cơ quan nào.*?:\s*\.{3,}", "Vào cơ quan: {{ co_quan_tuyen_dung }}"),
        (r"Ngày vào cơ quan hiện đang công tác:\s*\.{3,}", "Ngày vào cơ quan: {{ ngay_vao_co_quan }}"),
        (r"Ngày tham gia cách mạng:\s*\.{3,}", "Ngày tham gia cách mạng: {{ ngay_tham_gia_cach_mang }}"),
        
        # Mục 14-16: Đảng, quân đội
        (r"Ngày chính thức:\s*\.{3,}", "Ngày chính thức: {{ ngay_chinh_thuc_dang }}"),
        (r"Ngày tham gia các tổ chức.*?:\s*\.{3,}", "Ngày tham gia tổ chức: {{ ngay_tham_gia_to_chuc }}"),
        (r"Ngày nhập ngũ:\s*\.{3,}", "Ngày nhập ngũ: {{ ngay_nhap_ngu }}"),
        (r"Ngày xuất ngũ:\s*\.{3,}", "Ngày xuất ngũ: {{ ngay_xuat_ngu }}"),
        (r"Quân hàm.*?:\s*\.{3,}", "Quân hàm: {{ quan_ham }}"),
        
        # Mục 17: Học vấn
        (r"Giáo dục phổ thông:\s*\.{3,}", "Giáo dục phổ thông: {{ trinh_do_giao_duc_pho_thong }}"),
        (r"Học hàm, học vị.*?:\s*\.{3,}", "Học hàm, học vị: {{ hoc_ham_hoc_vi }}"),
        (r"- Lý luận chính trị:\s*\.{3,}", "- Lý luận chính trị: {{ ly_luan_chinh_tri }}"),
        (r"- Ngoại ngữ:\s*\.{3,}", "- Ngoại ngữ: {{ ngoai_ngu }}"),
        (r"Quản lý nhà nước:\s*\.{3,}", "Quản lý nhà nước: {{ quan_ly_nha_nuoc }}"),
        (r"Tin học:\s*\.{3,}", "Tin học: {{ tin_hoc }}"),
        
        # Mục 18-21: Công tác
        (r"Công tác chính đang làm:\s*\.{3,}", "Công tác chính: {{ cong_tac_chinh }}"),
        (r"Ngạch công chức:\s*\.{3,}", "Ngạch công chức: {{ ngach_cong_chuc }}"),
        (r"\(mã số:\s*\.{3,}", "(mã số: {{ ma_ngach }}"),
        (r"Bậc lương:\s*\.{3,}", "Bậc lương: {{ bac_luong }}"),
        (r"hệ số:\s*\.{3,}", "hệ số: {{ he_so_luong }}"),
        (r"từ tháng\s*\.{3,}", "từ tháng: {{ tu_thang_nam }}"),
        (r"Danh hiệu được phong.*?:\s*\.{3,}", "Danh hiệu: {{ danh_hieu }}"),
        (r"Sở trường công tác:\s*\.{3,}", "Sở trường: {{ so_truong_cong_tac }}"),
        (r"Công việc đã làm lâu nhất:\s*\.{3,}", "Công việc lâu nhất: {{ cong_viec_lau_nhat }}"),
        
        # Mục 22-25
        (r"Khen thưởng:\s*\.{3,}", "Khen thưởng: {{ khen_thuong }}"),
        (r"Kỷ luật.*?:\s*\.{3,}", "Kỷ luật: {{ ky_luat }}"),
        (r"Tình trạng sức khỏe:\s*\.{3,}", "Sức khỏe: {{ suc_khoe }}"),
        (r"Cao:\s*1m\s*\.{3,}", "Cao: {{ chieu_cao }}"),
        (r"Cân nặng:\s*\.{3,}", "Cân nặng: {{ can_nang }}"),
        (r"Nhóm máu:\s*\.{3,}", "Nhóm máu: {{ nhom_mau }}"),
        (r"Số chứng minh nhân dân:\s*\.{3,}", "Số CMND: {{ so_cmnd }}"),
        (r"Ngày cấp:\s*\.{3,}", "Ngày cấp: {{ ngay_cap }}"),
        (r"Nơi cấp:\s*\.{3,}", "Nơi cấp: {{ noi_cap }}"),
        (r"Thương binh loại:\s*\.{3,}", "Thương binh: {{ thuong_binh_loai }}"),
        (r"Gia đình liệt sĩ:\s*\.{3,}", "Gia đình liệt sĩ: {{ gia_dinh_liet_si }}"),
        
        # Mục 26-31: Gia đình
        (r"Tình trạng hôn nhân:\s*\.{3,}", "Hôn nhân: {{ tinh_trang_hon_nhan }}"),
        (r"Họ và tên vợ.*?:\s*\.{3,}", "Họ và tên vợ (chồng): {{ ten_vo_chong }}"),
        (r"Năm sinh:\s*\.{3,}", "Năm sinh: {{ nam_sinh_vo_chong }}"),
        (r"Quê quán:\s*\.{3,}", "Quê quán: {{ que_quan_vo_chong }}"),
        (r"Nghề nghiệp:\s*\.{3,}", "Nghề nghiệp: {{ nghe_nghiep_vo_chong }}"),
        (r"Chỗ ở:\s*\.{3,}", "Chỗ ở: {{ cho_o_vo_chong }}"),
        
        # Kinh tế
        (r"\+ lương:\s*\.{3,}", "+ Lương: {{ nguon_thu_luong }}"),
        (r"\+ Các nguồn khác:\s*\.{3,}", "+ Nguồn khác: {{ nguon_thu_khac }}"),
        (r"\+ Được cấp.*?:\s*\.{3,}", "+ Được cấp: {{ nha_o_duoc_cap }}"),
        (r"\+ Nhà tự mua.*?:\s*\.{3,}", "+ Tự mua: {{ nha_o_tu_mua }}"),
        (r"\+ Đất được cấp:\s*\.{3,}", "+ Đất cấp: {{ dat_o_duoc_cap }}"),
        (r"\+ Đất tự mua:\s*\.{3,}", "+ Đất mua: {{ dat_o_tu_mua }}"),
        (r"Đất sản xuất.*?:\s*\.{3,}", "Đất sản xuất: {{ dat_san_xuat }}"),
        
        # Chữ ký
        (r"Ngày\s+\.{3,}\s+tháng\s+\.{3,}\s+năm\s+20\.{2,}", "Ngày {{ ngay_ky }} tháng {{ thang_ky }} năm {{ nam_ky }}"),
    ]
    
    # Apply to paragraphs
    print("\n🔧 Cập nhật paragraphs...")
    count = 0
    
    for para in doc.paragraphs:
        original = para.text
        new_text = original
        
        for pattern, replacement in replacements:
            new_text = re.sub(pattern, replacement, new_text, flags=re.IGNORECASE)
        
        if new_text != original:
            para.text = new_text
            count += 1
            print(f"   ✓ {original[:40]}... → {new_text[:40]}...")
    
    print(f"\n✅ Đã cập nhật {count} paragraphs")
    
    # Save
    output_path = Path("mau_2c_template_FULL_MAPPING.docx")
    doc.save(str(output_path))
    
    file_size = output_path.stat().st_size
    
    print("\n" + "="*80)
    print("✅ ĐÃ TẠO TEMPLATE MỚI!")
    print(f"📄 File: {output_path}")
    print(f"📊 Size: {file_size:,} bytes ({file_size/1024:.2f} KB)")
    print(f"💡 Mapping: {count} fields được cập nhật")
    print("\n🎯 Test ngay: python test_docxtpl.py")
    
    return True

if __name__ == "__main__":
    try:
        update_template_with_correct_mapping()
    except Exception as e:
        print(f"\n❌ LỖI: {e}")
        import traceback
        traceback.print_exc()
