# HƯỚNG DẪN TEST TÍNH NĂNG KIỂM TRA THỂ THỨC VĂN BẢN

## 📋 Danh sách văn bản mẫu

### ✅ Văn bản CHUẨN (để test detection tốt):

1. **1_VAN_BAN_CHUAN.txt** - Quyết định chuẩn 100%
   - Đầy đủ 10 thành phần thể thức
   - Đúng định dạng số ký hiệu: 123/QĐ-UBND
   - Có đủ căn cứ pháp lý
   - Nơi nhận đầy đủ, có "Lưu: VP, VT"
   - **Kỳ vọng: 95-100 điểm**

2. **4_VAN_BAN_CHUAN_2.txt** - Tờ trình chuẩn
   - Đầy đủ thể thức tờ trình
   - Có "Kính trình" ở đúng vị trí
   - Nội dung có cấu trúc rõ ràng (4 phần)
   - **Kỳ vọng: 90-100 điểm**

---

### ❌ Văn bản CÓ LỖI (để test error detection):

3. **2_VAN_BAN_LOI_1.txt** - Công văn có 3 lỗi
   - **Lỗi 1**: Số ký hiệu sai "456/CV-UBND" (công văn thường không có CV)
   - **Lỗi 2**: Ngày tháng sai định dạng "31/12/2025" (phải viết đầy đủ)
   - **Lỗi 3**: Thiếu dấu gạch ngang dưới tiêu ngữ
   - **Lỗi 4**: Nơi nhận thiếu "Lưu: VP"
   - **Kỳ vọng: 60-70 điểm, 4 vi phạm được phát hiện**

4. **3_VAN_BAN_LOI_2.txt** - Báo cáo có nhiều lỗi
   - **Lỗi 1**: Số ký hiệu sai định dạng "UBND-789-BC" (phải "789/BC-UBND")
   - **Lỗi 2**: Thiếu dấu gạch ngang phân cách cơ quan
   - **Lỗi 3**: Thiếu chức vụ trước chữ ký (chỉ có tên)
   - **Lỗi 4**: Nơi nhận không đúng thứ tự (thiếu "Như Điều X")
   - **Kỳ vọng: 50-65 điểm, 4+ vi phạm**

---

## 🧪 Cách test

### Bước 1: Khởi động hệ thống
```bash
# Terminal 1: Backend
cd backend
python -m uvicorn app.main_simple:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Frontend
cd frontend
npm run dev
```

### Bước 2: Login và truy cập
1. Đăng nhập: http://localhost:5173/login
2. Vào trang kiểm tra: http://localhost:5173/user/kiem-tra-the-thuc
3. Hoặc click card "Kiểm tra thể thức VB" trên Dashboard

### Bước 3: Test từng văn bản

**Test 1: Văn bản chuẩn (1_VAN_BAN_CHUAN.txt)**
- Upload file
- Chờ 10-15 giây (Gemini xử lý)
- **Expected result:**
  ```
  Điểm: 95-100/100
  ✅ Không vi phạm hoặc vi phạm nhỏ
  Đạt: quoc_hieu, tieu_ngu, so_ky_hieu, ngay_thang, ...
  ```

**Test 2: Công văn lỗi (2_VAN_BAN_LOI_1.txt)**
- Upload file
- **Expected result:**
  ```
  Điểm: 60-70/100
  ❌ Vi phạm:
  - Số ký hiệu: Dùng "456/CV-UBND" thay vì "456/UBND-VP"
  - Ngày tháng: Dùng "31/12/2025" thay vì "ngày 31 tháng 12 năm 2025"
  - Nơi nhận: Thiếu "Lưu: VP, VT"
  ```

**Test 3: Báo cáo lỗi nhiều (3_VAN_BAN_LOI_2.txt)**
- Upload file
- **Expected result:**
  ```
  Điểm: 50-65/100
  ❌ Vi phạm:
  - Số ký hiệu: Sai định dạng "UBND-789-BC", phải "789/BC-UBND"
  - Chức vụ: Thiếu chức vụ trước chữ ký
  - Nơi nhận: Không đúng thứ tự
  ```

**Test 4: Tờ trình chuẩn (4_VAN_BAN_CHUAN_2.txt)**
- Upload file
- **Expected result:**
  ```
  Điểm: 90-100/100
  Loại văn bản: TO_TRINH
  ✅ Có "Kính trình" đúng vị trí
  ✅ Nội dung có cấu trúc 4 phần rõ ràng
  ```

---

## 📊 Metrics cần tracking

### 1. Accuracy (Độ chính xác)
- Văn bản chuẩn → Phải cho điểm ≥ 90
- Văn bản lỗi → Phát hiện được ít nhất 70% lỗi thực tế

### 2. Performance (Hiệu suất)
- Thời gian xử lý: 10-20 giây/văn bản
- AI cost: ~$0.02-0.05/văn bản (Gemini 2.0 Flash)

### 3. Usability (Trải nghiệm)
- Loading state rõ ràng
- Kết quả dễ đọc, có gợi ý sửa
- Không bị lỗi khi upload file lớn (< 10MB)

---

## 🐛 Các lỗi có thể gặp & cách fix

### Lỗi 1: "Không thể trích xuất nội dung văn bản"
**Nguyên nhân:** File bị lỗi hoặc định dạng không hỗ trợ
**Fix:** Kiểm tra file có đúng .txt/.pdf/.docx không

### Lỗi 2: "AI trả về dữ liệu không hợp lệ"
**Nguyên nhân:** Gemini không trả về JSON đúng format
**Fix:** 
- Kiểm tra GEMINI_API_KEY trong .env
- Xem log backend để debug prompt
- Có thể cần adjust prompt (trong vb_checker_prompts.py)

### Lỗi 3: "403 Quota exceeded"
**Nguyên nhân:** User hết quota AI
**Fix:** 
- Kiểm tra subscription của user
- Tạm thời tăng quota trong database:
  ```sql
  UPDATE users SET ai_quota_monthly = 1000 WHERE email = 'test@example.com';
  ```

### Lỗi 4: "500 Internal Server Error"
**Nguyên nhân:** Backend crash
**Fix:**
- Xem log terminal backend
- Kiểm tra database đã migrate chưa
- Chạy lại: `python scripts/create_tables.py`

---

## ✅ Checklist trước khi demo cho user

- [ ] Backend chạy không lỗi
- [ ] Frontend hiển thị đẹp, responsive
- [ ] Test ít nhất 3 văn bản (1 chuẩn, 2 lỗi)
- [ ] Kết quả chính xác ≥ 80%
- [ ] Thời gian xử lý < 30 giây
- [ ] Toast notification hoạt động
- [ ] Loading state rõ ràng
- [ ] Error handling tốt (không crash)

---

## 🎯 Next steps nếu test thành công

1. **Thu thập feedback từ 5-10 user thực tế** (cán bộ văn thư)
2. **Fine-tune prompt** dựa trên feedback:
   - Nếu accuracy < 85% → Adjust prompt thêm examples
   - Nếu bỏ sót lỗi → Thêm rule check
3. **Tối ưu performance:**
   - Cache kết quả văn bản đã check
   - Batch processing nếu upload nhiều file
4. **Thêm tính năng:**
   - Export báo cáo PDF
   - Lịch sử các văn bản đã check
   - So sánh 2 phiên bản văn bản

---

## 📞 Support

Nếu gặp vấn đề khi test:
1. Check backend logs (terminal chạy uvicorn)
2. Check frontend console (F12 trong browser)
3. Check database: `psql -U utility_user -d utility_db -h 165.99.59.47`
4. Ping me với screenshot lỗi!
