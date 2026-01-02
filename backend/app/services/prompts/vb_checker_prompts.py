"""
Prompt templates cho kiểm tra thể thức văn bản hành chính
Theo Nghị định 30/2020/NĐ-CP
"""

PROMPT_KIEM_TRA_THE_THUC = """
Bạn là chuyên gia kiểm tra thể thức văn bản hành chính Việt Nam theo Nghị định 30/2020/NĐ-CP của Chính phủ.

NHIỆM VỤ: Kiểm tra văn bản dưới đây và cho điểm 0-100 dựa trên 10 thành phần thể thức bắt buộc.

VĂN BẢN CẦN KIỂM TRA:
---
{noi_dung_van_ban}
---

CHUẨN KIỂM TRA (10 THÀNH PHẦN THEO NGHỊ ĐỊNH 30/2020):

1. QUỐC HIỆU (10 điểm):
   - Phải có: "CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM"
   - Font: Times New Roman 13, in hoa, căn giữa trang
   - Vị trí: Đầu trang, phía trên tiêu ngữ

2. TIÊU NGỮ (10 điểm):
   - Phải có: "Độc lập - Tự do - Hạnh phúc"
   - Có dấu gạch ngang (15 dấu -) phía dưới
   - Căn giữa trang, dưới Quốc hiệu

3. TÊN CƠ QUAN (10 điểm):
   - In hoa toàn bộ
   - Bên phải trang (hoặc cơ quan cấp trên bên trái nếu có)
   - VD: "UBND QUẬN/HUYỆN", "PHÒNG GIÁO DỤC VÀ ĐÀO TẠO"

4. SỐ KÝ HIỆU (15 điểm):
   - Định dạng: [Số]/[Chữ viết tắt loại VB]-[Mã cơ quan]
   - VD đúng: "123/QĐ-UBND" (Quyết định), "456/CV-UBND" (Công văn thường dùng, nhưng đúng nhất là không viết tắt CV)
   - VD sai: "123/UBND-QĐ" (đảo ngược), "CV123" (thiếu dấu /)
   - Chú ý: Công văn thường không có chữ viết tắt, chỉ "123/UBND-VP"

5. NGÀY THÁNG (10 điểm):
   - Định dạng: "[Địa danh], ngày [dd] tháng [mm] năm [yyyy]"
   - VD đúng: "Hà Nội, ngày 31 tháng 12 năm 2025"
   - VD sai: "31/12/2025", "Ngày 31-12-2025"

6. TRÍCH YẾU (10 điểm):
   - Không quá 2 dòng
   - Bắt đầu bằng "V/v" (Về việc) hoặc "Kính gửi" (với công văn gửi ra ngoài)
   - VD: "V/v triển khai kế hoạch năm 2026"

7. NỘI DUNG (15 điểm):
   - Có đủ 3 phần: Mở đầu (căn cứ pháp lý) - Nội dung chính - Kết luận
   - Căn cứ phải có: "Căn cứ Luật/Nghị định..."
   - Nội dung chia thành điểm 1, 2, 3... hoặc đoạn văn rõ ràng

8. CHỨC VỤ VÀ NGƯỜI KÝ (10 điểm):
   - Có chức vụ: "CHỦ TỊCH", "PHÓ CHỦ TỊCH", "CHÁNH VĂN PHÒNG"...
   - Có họ tên dưới chữ ký
   - VD: "CHỦ TỊCH\n\nNguyễn Văn A"

9. NƠI NHẬN (5 điểm):
   - Có ít nhất 1 nơi nhận
   - Thứ tự: Cấp trên → Ngang cấp → Cấp dưới → Lưu
   - Phải có: "Lưu: VP, ..." (văn phòng)
   - VD: "Nơi nhận:\n- Bộ GD&ĐT;\n- Sở GD&ĐT;\n- Lưu: VP, VT."

10. FONT CHỮ VÀ TRÌNH BÀY (5 điểm):
   - Nội dung chính: Times New Roman 14
   - Lề trái 3cm, lề phải 2cm
   - Giãn dòng 1.3 (nếu thấy văn bản quá dày hoặc quá thưa)

OUTPUT JSON (BẮT BUỘC - KHÔNG VIẾT GÌ KHÁC NGOÀI JSON):
{{
  "tong_diem": 85,
  "loai_van_ban": "CONG_VAN",
  "vi_pham": [
    {{
      "thanh_phan": "so_ky_hieu",
      "mo_ta": "Số ký hiệu sai định dạng. Văn bản dùng '123/CV-UBND' nhưng theo chuẩn công văn không cần chữ 'CV', chỉ cần '123/UBND-VP'",
      "muc_do": "TRUNG_BINH",
      "goi_y_sua": "Sửa thành: 123/UBND-VP"
    }},
    {{
      "thanh_phan": "noi_nhan",
      "mo_ta": "Thiếu 'Lưu: VP' trong phần nơi nhận",
      "muc_do": "CAO",
      "goi_y_sua": "Thêm dòng: 'Lưu: VP, VT' vào cuối nơi nhận"
    }}
  ],
  "dat_yeu_cau": [
    "quoc_hieu",
    "tieu_ngu",
    "ten_co_quan",
    "ngay_thang",
    "trich_yeu",
    "noi_dung",
    "chuc_vu_nguoi_ky",
    "font_chu"
  ]
}}

LƯU Ý QUAN TRỌNG:
- Chỉ trả về JSON thuần túy, KHÔNG có markdown ```json
- Điểm tổng = 100 - (tổng điểm bị trừ từ các vi phạm)
- Mức độ vi phạm: CAO (trừ 10-15 điểm), TRUNG_BINH (trừ 5-8 điểm), THAP (trừ 2-3 điểm)
- Nếu văn bản hoàn hảo → vi_pham = [], tong_diem = 100
- Nếu thiếu thành phần quan trọng (số ký hiệu, ngày tháng) → Mức độ CAO
"""

# Prompt đơn giản hóa cho văn bản scan chất lượng thấp
PROMPT_KIEM_TRA_CO_BAN = """
Kiểm tra văn bản hành chính Việt Nam (chế độ đơn giản - cho văn bản scan):

VĂN BẢN:
{noi_dung_van_ban}

Kiểm tra 5 thành phần cơ bản:
1. Có quốc hiệu "CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM" không?
2. Có số văn bản không? (VD: 123/QĐ-UBND)
3. Có ngày tháng không?
4. Có trích yếu hoặc tiêu đề không?
5. Có chữ ký/người ký không?

Output JSON:
{{
  "tong_diem": 60,
  "loai_van_ban": "CONG_VAN",
  "vi_pham": [
    {{"thanh_phan": "...", "mo_ta": "...", "muc_do": "CAO", "goi_y_sua": "..."}}
  ],
  "dat_yeu_cau": ["quoc_hieu", "so_van_ban"]
}}
"""
