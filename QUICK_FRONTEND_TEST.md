# Hướng Dẫn Test Frontend - Phiên Bản Nhanh

## 🚀 Truy Cập Ngay

### Mở trình duyệt và vào:
```
http://165.99.59.47
```

## ✅ Test Nhanh 5 Phút

### 1️⃣ Test Trang Chủ (10 giây)
- Mở: `http://165.99.59.47`
- ✓ Trang load được không?
- ✓ Logo và menu hiển thị không?
- ✓ Nhấn F12 → Console có lỗi không?

### 2️⃣ Test Login (30 giây)
- Vào: `http://165.99.59.47/login`
- Nhập:
  ```
  Username: admin
  Password: admin123
  ```
- ✓ Login được không?
- ✓ Redirect về dashboard không?

### 3️⃣ Test Upload File (1 phút)
- Vào phần Upload hoặc Dashboard
- Chọn file PDF/Image/Word bất kỳ
- ✓ Upload thành công không?
- ✓ File xuất hiện trong danh sách không?

### 4️⃣ Test Convert PDF (1 phút)
- Upload 1 file PDF
- Chọn "Convert to Word" hoặc "Convert to Image"
- ✓ Conversion chạy không?
- ✓ Download file kết quả được không?
- ✓ Mở file kết quả xem đúng không?

### 5️⃣ Test OCR (1 phút)
- Upload 1 ảnh có chữ (tiếng Việt hoặc tiếng Anh)
- Chọn "Extract Text" hoặc "OCR"
- ✓ Text được extract ra không?
- ✓ Text đúng không?
- ✓ Dấu tiếng Việt đúng không?

### 6️⃣ Test Responsive (30 giây)
- Nhấn F12 → Click icon mobile
- Hoặc resize browser window
- ✓ Layout không bị vỡ trên mobile?
- ✓ Menu collapse đúng không?

## 📱 Test Trên Điện Thoại

### Cách 1: Dùng WiFi cùng mạng
```
http://165.99.59.47
```

### Cách 2: Dùng 4G/5G
```
http://165.99.59.47
```

**Kiểm tra:**
- ✓ Touch scroll mượt không?
- ✓ Button dễ bấm không?
- ✓ Upload file từ camera/gallery được không?

## 🔥 Test Nhanh Bằng Terminal

### Test 1: Frontend có online không?
```bash
curl -I http://165.99.59.47/
```
**Mong đợi:** `HTTP/1.1 200 OK`

### Test 2: Backend API có hoạt động không?
```bash
curl http://165.99.59.47/health
```
**Mong đợi:** `{"status":"healthy","version":"1.0.0"}`

### Test 3: Upload test
```bash
# Tạo file test
echo "Test content" > test.txt

# Upload (cần token)
curl -X POST http://165.99.59.47/api/documents/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@test.txt"
```

### Test 4: Check performance
```bash
# Đo thời gian load
time curl -s -o /dev/null http://165.99.59.47/

# Mong đợi: < 2 seconds
```

## 🎯 Test Cases Quan Trọng

### Must-Have (Bắt buộc phải test)
- [ ] **Homepage load** - Không 404 hay 500
- [ ] **Login hoạt động** - Admin login được
- [ ] **Upload PDF** - Upload và list files
- [ ] **Convert PDF to Word** - Chạy được và download
- [ ] **OCR tiếng Việt** - Nhận dấu đúng

### Nice-to-Have (Nên test thêm)
- [ ] **Responsive** - Mobile/tablet
- [ ] **Image processing** - Resize, crop, rotate
- [ ] **Admin dashboard** - Stats hiển thị
- [ ] **Error handling** - Upload file quá lớn
- [ ] **Performance** - Load < 2s

## 🐛 Nếu Có Lỗi

### Lỗi 1: Trang không load (404)
```bash
# Check Nginx logs
ssh root@165.99.59.47 "docker logs utility_nginx --tail=50"

# Restart Nginx
ssh root@165.99.59.47 "docker-compose restart nginx"
```

### Lỗi 2: API lỗi (500)
```bash
# Check backend logs
ssh root@165.99.59.47 "docker logs utility_backend --tail=50"

# Restart backend
ssh root@165.99.59.47 "docker-compose restart backend"
```

### Lỗi 3: Upload không được
- Check file size < 50MB
- Check file type cho phép (PDF, DOCX, XLSX, JPG, PNG)
- Check đã login chưa (có token chưa)

### Lỗi 4: Slow performance
```bash
# Check server resources
ssh root@165.99.59.47 "docker stats --no-stream"

# Check memory
ssh root@165.99.59.47 "free -h"
```

## 📊 Dashboard Admin Test

### URL:
```
http://165.99.59.47/admin
hoặc
http://165.99.59.47/dashboard
```

### Login:
```
Username: admin
Password: admin123
```

### Kiểm tra:
- [ ] Total users count
- [ ] Total uploads count
- [ ] Storage used (MB/GB)
- [ ] API calls today
- [ ] Recent activity logs
- [ ] User list (với edit/delete buttons)

## 🎨 Visual Tests

### Kiểm tra UI/UX:
1. **Colors** - Màu sắc đẹp, dễ nhìn
2. **Fonts** - Chữ rõ ràng, dễ đọc
3. **Buttons** - Hover effect, click feedback
4. **Forms** - Labels rõ ràng, validation messages
5. **Loading** - Spinners/progress bars khi process

### Kiểm tra Accessibility:
- Tab navigation works
- Focus visible trên inputs
- Alt text cho images
- Error messages rõ ràng

## 💡 Tips Test Hiệu Quả

### 1. Test theo workflow thực tế:
```
Login → Upload PDF → Convert to Word → Download → Verify
```

### 2. Test với data thật:
- File PDF thật (không phải dummy file)
- Image có text tiếng Việt thật
- File size khác nhau (1KB → 10MB)

### 3. Test các edge cases:
- File name có ký tự đặc biệt
- File rất lớn (>50MB - should reject)
- File không đúng format (.exe - should reject)
- Nhiều files cùng lúc (batch upload)

### 4. Test performance:
- Upload nhiều files liên tiếp
- Convert nhiều PDFs đồng thời
- Check memory không leak

## ✨ Kết Quả Mong Đợi

### ✅ PASS Criteria:
- [ ] All pages load < 2s
- [ ] No 404/500 errors
- [ ] Login successful
- [ ] Upload works for all file types
- [ ] Convert PDF works
- [ ] OCR Vietnamese works
- [ ] Responsive on mobile
- [ ] No console errors

### ❌ FAIL Criteria:
- Pages không load
- Lỗi 500 khi upload
- OCR không nhận tiếng Việt
- Layout vỡ trên mobile
- Memory leak (browser crash)

## 📞 Cần Trợ Giúp?

### Debug Steps:
1. F12 → Console tab (check errors)
2. F12 → Network tab (check failed requests)
3. F12 → Application tab (check storage/cookies)
4. Check backend logs: `docker logs utility_backend`
5. Check Nginx logs: `docker logs utility_nginx`

### Common Solutions:
```bash
# Restart all services
ssh root@165.99.59.47 "cd /opt/utility-server && docker-compose restart"

# Check all containers running
ssh root@165.99.59.47 "docker ps"

# Check system resources
ssh root@165.99.59.47 "df -h && free -h"
```

---

## 🎯 Checklist Cuối Cùng

```
□ Homepage loads ✓
□ Login works ✓
□ Upload PDF works ✓
□ Convert PDF works ✓
□ OCR Vietnamese works ✓
□ Admin dashboard accessible ✓
□ Mobile responsive ✓
□ No console errors ✓
□ Performance good (<2s load) ✓
```

**Nếu tất cả đều ✓ → Frontend sẵn sàng production! 🎉**

---

**Quick Start:** Mở `http://165.99.59.47` → Login admin/admin123 → Test upload PDF → Done!

**Prepared by:** GitHub Copilot  
**Date:** 2025-11-21 23:15:00 +07:00
