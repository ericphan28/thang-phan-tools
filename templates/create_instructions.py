"""
HƯỚNG DẪN TẠO TEMPLATE MẪU 2C THỦ CÔNG
========================================

BƯỚC 1: Mở file gốc trong Word
-------------------------------
- Mở file: templates\mau-nha-nuoc\Mau-ly-lich-2C-TCTW-98.docx
- Lưu bản sao mới: templates\mau_2c_template_manual.docx

BƯỚC 2: Thay thế các dấu chấm bằng {{variables}}
-------------------------------------------------
Dùng Find & Replace (Ctrl+H) trong Word:

** PHẦN HEADER **
Tìm: Tỉnh: …………………
Thay: Tỉnh: {{tinh}}

Tìm: Đơn vị trực thuộc: .........................
Thay: Đơn vị trực thuộc: {{don_vi_truc_thuoc}}

Tìm: Đơn vị cơ sở: ................................
Thay: Đơn vị cơ sở: {{don_vi_co_so}}

** MỤC 1-5 **
1) Họ và tên khai sinh: ……………………………………..
   → Họ và tên khai sinh: {{ho_ten}}
   
   Nam, nữ: ...............
   → Nam, nữ: {{gioi_tinh}}

2) Các tên gọi khác: ................................................
   → Các tên gọi khác: {{ten_khac}}

3) Cấp ủy hiện tại: .......................................
   → Cấp ủy hiện tại: {{cap_uy}}
   
   Cấp ủy kiêm: .........................................
   → Cấp ủy kiêm: {{cap_uy_kiem}}

   Chức vụ (Đảng, đoàn thể...): ................................................
   → Chức vụ (Đảng, đoàn thể, Chính quyền, kể cả chức vụ kiêm nhiệm): {{chuc_vu}}
   
   Phụ cấp chức vụ: ...........................
   → Phụ cấp chức vụ: {{phu_cap}}

4) Sinh ngày: .......... tháng .......... năm ...............
   → Sinh ngày: {{ngay}} tháng {{thang}} năm {{nam}}

5) Nơi sinh: ..................................................
   → Nơi sinh: {{noi_sinh}}

** MỤC 6-10 **
6) Quê quán (xã, phường): .......................................
   → Quê quán (xã, phường): {{que_xa}}
   
   (huyện, quận): ........................
   → (huyện, quận): {{que_huyen}}
   
   (tỉnh, TP): ...............................
   → (tỉnh, TP): {{que_tinh}}

7) Nơi ở hiện nay (Xã, huyện, tỉnh...): ............
   → Nơi ở hiện nay (Xã, huyện, tỉnh hoặc số nhà, đường phố, TP): {{dia_chi}}
   
   đ/thoại: ....................
   → đ/thoại: {{dien_thoai}}

8) Dân tộc: (Kinh, Tày, Mông, Ê đê...): ....................................
   → Dân tộc: {{dan_toc}}

9) Tôn giáo: ......................................................
   → Tôn giáo: {{ton_giao}}

10) Thành phần gia đình xuất thân: ........................................
    → Thành phần gia đình xuất thân: {{thanh_phan}}

** MỤC 11-15 **
11) Nghề nghiệp bản thân trước khi được tuyển dụng: ................
    → Nghề nghiệp bản thân trước khi được tuyển dụng: {{nghe_truoc}}

12) Ngày được tuyển dụng: ......... / ........... / ..........
    → Ngày được tuyển dụng: {{ngay_tuyen_dung}}
    
    Vào cơ quan nào, ở đâu: .............................................
    → Vào cơ quan nào, ở đâu: {{co_quan_tuyen_dung}}

13) Ngày vào cơ quan hiện đang công tác: ...... / ....... / ......
    → Ngày vào cơ quan hiện đang công tác: {{ngay_vao_co_quan}}
    
    Ngày tham gia cách mạng: ...... / ....... / ........
    → Ngày tham gia cách mạng: {{ngay_cach_mang}}

14) Ngày vào Đảng Cộng sản Việt Nam: ......... / .......... / ........
    → Ngày vào Đảng Cộng sản Việt Nam: {{ngay_vao_dang}}
    
    Ngày chính thức: ........ / .......... / ..............
    → Ngày chính thức: {{ngay_chinh_thuc}}

15) Ngày tham gia các tổ chức chính trị, xã hội: ........................
    → Ngày tham gia các tổ chức chính trị, xã hội: {{to_chuc}}

** MỤC 16-20 **
16) Ngày nhập ngũ: ... / ... / ....
    → Ngày nhập ngũ: {{ngay_nhap_ngu}}
    
    Ngày xuất ngũ: ... / ... / .....
    → Ngày xuất ngũ: {{ngay_xuat_ngu}}
    
    Quân hàm, chức vụ cao nhất (năm): ............................
    → Quân hàm, chức vụ cao nhất (năm): {{quan_ham}}

17) Trình độ học vấn: Giáo dục phổ thông: ..............
    → Trình độ học vấn: Giáo dục phổ thông: {{hoc_van}}
    
    Học hàm, học vị cao nhất: .................................................
    → Học hàm, học vị cao nhất: {{hoc_vi}}
    
    - Lý luận chính trị: ...............................
    → - Lý luận chính trị: {{ly_luan}}
    
    - Ngoại ngữ: ............
    → - Ngoại ngữ: {{ngoai_ngu}}

18) Công tác chính đang làm: ........................................
    → Công tác chính đang làm: {{cong_tac}}

19) Ngạch công chức: ..................... (mã số: .................)
    → Ngạch công chức: {{ngach}} (mã số: {{ma_ngach}})
    
    Bậc lương: .........., hệ số: ........... từ tháng .... /.........
    → Bậc lương: {{bac}}, hệ số: {{he_so}} từ tháng {{thang_luong}}

20) Danh hiệu được phong (năm nào): ........................................
    → Danh hiệu được phong (năm nào): {{danh_hieu}}

** MỤC 21-25 **
21) Sở trường công tác: .........................................
    → Sở trường công tác: {{so_truong}}
    
    Công việc đã làm lâu nhất: ..........................................
    → Công việc đã làm lâu nhất: {{cv_lau_nhat}}

22) Khen thưởng: ........................................................
    → Khen thưởng: {{khen_thuong}}

23) Kỷ luật (Đảng, Chính quyền, Đoàn thể...): ...................................................
    → Kỷ luật (Đảng, Chính quyền, Đoàn thể, Cấp quyết định, năm nào, lý do, hình thức, ...): {{ky_luat}}

24) Tình trạng sức khỏe: .........................................
    → Tình trạng sức khỏe: {{suc_khoe}}
    
    Cao: 1m ......, Cân nặng: ....... (kg), Nhóm máu: ........
    → Cao: {{chieu_cao}}, Cân nặng: {{can_nang}} (kg), Nhóm máu: {{nhom_mau}}

25) Số chứng minh nhân dân: .................................
    → Số chứng minh nhân dân: {{cmnd}}
    
    Thương binh loại: ..................
    → Thương binh loại: {{thuong_binh}}
    
    Gia đình liệt sĩ:
    → Gia đình liệt sĩ: {{liet_si}}

BƯỚC 3: XỬ LÝ 5 BẢNG
--------------------

** BẢNG 1: Đào tạo, bồi dưỡng (Mục 26) **
- GIỮ NGUYÊN hàng tiêu đề: Tên trường | Ngành học | Thời gian | Hình thức | Văn bằng
- Ở hàng dữ liệu (hàng 2), thay dấu chấm:
  + Cột 1: {{#dao_tao}}{{ten_truong}}{{/dao_tao}}
  + Cột 2: {{#dao_tao}}{{nganh_hoc}}{{/dao_tao}}
  + Cột 3: {{#dao_tao}}{{thoi_gian}}{{/dao_tao}}
  + Cột 4: {{#dao_tao}}{{hinh_thuc}}{{/dao_tao}}
  + Cột 5: {{#dao_tao}}{{van_bang}}{{/dao_tao}}

** BẢNG 2: Quá trình công tác (Mục 27) **
- GIỮ NGUYÊN tiêu đề: Từ tháng, năm đến tháng, năm | Chức danh, chức vụ...
- Hàng dữ liệu:
  + Cột 1: {{#cong_tac}}{{thoi_gian}}{{/cong_tac}}
  + Cột 2: {{#cong_tac}}{{chuc_vu_don_vi}}{{/cong_tac}}

** BẢNG 3: Gia đình bản thân (Mục 30a) **
⚠️ QUAN TRỌNG: Cột 1 đã có SẴN text "Bố, mẹ", "Vợ", "Chồng", "Các con", "Anh chị em ruột"
   → KHÔNG XÓA, CHỈ thay dấu chấm ở 3 cột còn lại:
   
- Cột 2 (Họ và tên): {{#gia_dinh}}{{ho_ten}}{{/gia_dinh}}
- Cột 3 (Năm sinh): {{#gia_dinh}}{{nam_sinh}}{{/gia_dinh}}
- Cột 4 (Quê quán, nghề nghiệp...): {{#gia_dinh}}{{thong_tin}}{{/gia_dinh}}

** BẢNG 4: Bố, Mẹ, anh chị em ruột (bên vợ/chồng) (Mục 30b) **
⚠️ Tương tự bảng 3, GIỮ NGUYÊN text "Bố, mẹ", "Anh chị em ruột" ở cột 1
- Cột 2: {{#gia_dinh_vo_chong}}{{ho_ten}}{{/gia_dinh_vo_chong}}
- Cột 3: {{#gia_dinh_vo_chong}}{{nam_sinh}}{{/gia_dinh_vo_chong}}
- Cột 4: {{#gia_dinh_vo_chong}}{{thong_tin}}{{/gia_dinh_vo_chong}}

** BẢNG 5: Quá trình lương (Mục 31) **
Đây là bảng ngang (timeline):
- Row 1: Tháng/năm: | 3/1993 | 4/1993 | ... 
  → Thay: {{#luong}}{{thang_nam}}{{/luong}}
  
- Row 2: Ngạch/bậc:
  → Thay: {{#luong}}{{ngach_bac}}{{/luong}}
  
- Row 3: Hệ số lương:
  → Thay: {{#luong}}{{he_so}}{{/luong}}

BƯỚC 4: Lưu file
----------------
- Lưu file: mau_2c_template_manual.docx
- Copy vào thư mục templates/

BƯỚC 5: Test
------------
python test_template_correct.py

==============================================================================
LƯU Ý QUAN TRỌNG
==============================================================================
1. ✅ PHẢI dùng Word desktop (không phải Word Online)
2. ✅ GIỮ NGUYÊN tất cả định dạng (font, size, spacing, borders)
3. ✅ GIỮ NGUYÊN labels trong bảng ("Bố, mẹ", "Vợ", "Chồng"...)
4. ✅ CHỈ thay dấu chấm (...) bằng {{variables}}
5. ✅ Dùng {{#array}}...{{/array}} cho dữ liệu lặp (bảng)
6. ⚠️ KHÔNG xóa bất kỳ text nào khác ngoài dấu chấm

==============================================================================
ADOBE DOCUMENT GENERATION SYNTAX
==============================================================================
- Simple variable: {{variable_name}}
- Loop (for table rows): {{#array_name}}{{field}}{{/array_name}}
- Condition: {{#if_variable}}text{{/if_variable}}
- Comment: {{!-- This is a comment --}}
"""
with open(r"d:\thang\utility-server\templates\HUONG_DAN_TAO_TEMPLATE.txt", "w", encoding="utf-8") as f:
    f.write(__doc__)

print("✅ Đã tạo file hướng dẫn: HUONG_DAN_TAO_TEMPLATE.txt")
print("\n📝 Vui lòng:")
print("   1. Mở file mau-nha-nuoc/Mau-ly-lich-2C-TCTW-98.docx trong Word")
print("   2. Làm theo hướng dẫn trong file HUONG_DAN_TAO_TEMPLATE.txt")
print("   3. Lưu thành mau_2c_template_manual.docx")
print("\n💡 Hoặc tôi có thể tạo script Python để copy file và bạn tự thay thế trong Word!")
