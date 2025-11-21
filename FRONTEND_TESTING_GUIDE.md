# Hướng Dẫn Test Frontend Trên Server

**Server:** 165.99.59.47  
**Ngày:** 2025-11-21

## 🌐 Truy Cập Frontend

### URL Chính
```
http://165.99.59.47
```

Hoặc nếu đã có domain:
```
https://your-domain.com
```

## ✅ Các Test Cases Cần Thực Hiện

### 1. Test Trang Chủ (Homepage)

**URL:** `http://165.99.59.47/`

**Kiểm tra:**
- [ ] Trang load thành công (không lỗi 404 hoặc 500)
- [ ] Logo và tiêu đề hiển thị đúng
- [ ] Menu navigation hiển thị
- [ ] CSS/styling load đúng (không bị lỗi style)
- [ ] Không có lỗi trong Console (F12)

**Lệnh test từ terminal:**
```bash
# Test HTTP response
curl -I http://165.99.59.47/

# Kết quả mong đợi: HTTP/1.1 200 OK
```

---

### 2. Test Trang Login

**URL:** `http://165.99.59.47/login`

**Kiểm tra:**
- [ ] Form login hiển thị đúng
- [ ] Input fields: username/email và password
- [ ] Button "Login" hoặc "Đăng nhập"
- [ ] Link "Forgot password" nếu có
- [ ] Link "Register" nếu có

**Test login với API:**
```bash
# Test login endpoint
curl -X POST http://165.99.59.47/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'

# Kết quả mong đợi: JWT token hoặc error message
```

---

### 3. Test Upload Files

**URL:** `http://165.99.59.47/upload` hoặc trong Dashboard

**Test các loại file:**

#### 3.1 Test Upload PDF
```bash
# Tạo file PDF test
echo "Test PDF content" > test.pdf

# Upload qua API
curl -X POST http://165.99.59.47/api/documents/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@test.pdf"

# Kết quả mong đợi: {"status":"success", "file_id":"..."}
```

**Kiểm tra:**
- [ ] Progress bar hiển thị khi upload
- [ ] Upload thành công với file < 10MB
- [ ] Thông báo thành công sau khi upload
- [ ] File xuất hiện trong danh sách

#### 3.2 Test Upload Image
```bash
# Upload image (PNG, JPG)
curl -X POST http://165.99.59.47/api/images/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@test.jpg"
```

**Kiểm tra:**
- [ ] Thumbnail preview hiển thị
- [ ] Upload các format: JPG, PNG, GIF, BMP
- [ ] File size limit warning nếu quá lớn

#### 3.3 Test Upload Document (Word, Excel)
```bash
# Upload Word file
curl -X POST http://165.99.59.47/api/documents/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@test.docx"

# Upload Excel file
curl -X POST http://165.99.59.47/api/documents/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@test.xlsx"
```

---

### 4. Test PDF Processing

#### 4.1 PDF to Word Conversion
**URL:** `http://165.99.59.47/convert/pdf-to-word`

**Test:**
```bash
# Convert PDF to Word
curl -X POST http://165.99.59.47/api/documents/pdf-to-word \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@document.pdf"
```

**Kiểm tra:**
- [ ] Upload PDF thành công
- [ ] Conversion progress hiển thị
- [ ] Download Word file thành công
- [ ] Word file mở được và có nội dung đúng

#### 4.2 PDF to Image
**Test:**
```bash
# Convert PDF to images
curl -X POST http://165.99.59.47/api/documents/pdf-to-images \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@document.pdf" \
  -F "format=png"
```

**Kiểm tra:**
- [ ] Tất cả pages được convert
- [ ] Images có quality tốt
- [ ] Download ZIP chứa tất cả images

#### 4.3 Merge PDFs
**Test:**
```bash
# Merge multiple PDFs
curl -X POST http://165.99.59.47/api/documents/merge-pdfs \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "files=@pdf1.pdf" \
  -F "files=@pdf2.pdf" \
  -F "files=@pdf3.pdf"
```

**Kiểm tra:**
- [ ] Upload nhiều files cùng lúc
- [ ] Drag & drop để sắp xếp thứ tự
- [ ] Merged PDF có đủ số trang
- [ ] Preview trước khi merge

---

### 5. Test Image Processing

#### 5.1 Image Resize
**URL:** `http://165.99.59.47/image/resize`

**Test:**
```bash
# Resize image
curl -X POST http://165.99.59.47/api/images/resize \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@image.jpg" \
  -F "width=800" \
  -F "height=600"
```

**Kiểm tra:**
- [ ] Input width và height
- [ ] Maintain aspect ratio option
- [ ] Preview before/after
- [ ] Download resized image

#### 5.2 Image Crop
**Test:**
```bash
# Crop image
curl -X POST http://165.99.59.47/api/images/crop \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@image.jpg" \
  -F "x=100" \
  -F "y=100" \
  -F "width=500" \
  -F "height=500"
```

**Kiểm tra:**
- [ ] Visual crop tool (drag to select area)
- [ ] Preview cropped area
- [ ] Download cropped image

#### 5.3 Image Rotate
**Test:**
```bash
# Rotate image
curl -X POST http://165.99.59.47/api/images/rotate \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@image.jpg" \
  -F "angle=90"
```

**Kiểm tra:**
- [ ] Rotate 90°, 180°, 270° buttons
- [ ] Custom angle input
- [ ] Preview rotation

#### 5.4 Image Format Conversion
**Test:**
```bash
# Convert image format
curl -X POST http://165.99.59.47/api/images/convert-format \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@image.jpg" \
  -F "output_format=png"
```

**Kiểm tra:**
- [ ] Convert JPG → PNG
- [ ] Convert PNG → JPG
- [ ] Convert BMP → PNG
- [ ] Convert GIF → PNG

---

### 6. Test OCR (Text Extraction)

#### 6.1 OCR from Image (English)
**URL:** `http://165.99.59.47/ocr/extract`

**Test:**
```bash
# Extract English text
curl -X POST http://165.99.59.47/api/ocr/extract \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@english_text.jpg" \
  -F "languages=eng"
```

**Kiểm tra:**
- [ ] Upload image có text tiếng Anh
- [ ] Text được extract chính xác
- [ ] Copy text to clipboard
- [ ] Download text file

#### 6.2 OCR from Image (Vietnamese)
**Test:**
```bash
# Extract Vietnamese text
curl -X POST http://165.99.59.47/api/ocr/extract-vietnamese \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@vietnamese_text.jpg"
```

**Kiểm tra:**
- [ ] Upload image có text tiếng Việt
- [ ] Dấu tiếng Việt được nhận dạng đúng
- [ ] Text format giữ nguyên (paragraph, line breaks)

#### 6.3 Auto-detect Language
**Test:**
```bash
# Auto detect and extract
curl -X POST http://165.99.59.47/api/ocr/detect-and-extract \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@mixed_text.jpg"
```

---

### 7. Test Admin Dashboard

**URL:** `http://165.99.59.47/admin` hoặc `/dashboard`

**Kiểm tra:**
- [ ] Login với admin credentials
- [ ] Statistics hiển thị:
  - Total users
  - Total uploads
  - Storage used
  - API calls today
- [ ] User management:
  - View all users
  - Edit user
  - Disable/Enable user
  - Delete user
- [ ] Activity logs hiển thị
- [ ] System health status

**Test Admin API:**
```bash
# Get user stats
curl -X GET http://165.99.59.47/api/users/stats \
  -H "Authorization: Bearer ADMIN_TOKEN"

# Get all users
curl -X GET http://165.99.59.47/api/users/ \
  -H "Authorization: Bearer ADMIN_TOKEN"

# Get activity logs
curl -X GET http://165.99.59.47/api/logs/activity \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

---

### 8. Test Error Handling

#### 8.1 Test Large File Upload
```bash
# Try upload file > 50MB (should fail gracefully)
curl -X POST http://165.99.59.47/api/documents/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@large_file.pdf"

# Kết quả mong đợi: Error message "File too large"
```

**Kiểm tra:**
- [ ] Error message hiển thị rõ ràng
- [ ] UI không bị crash
- [ ] User có thể retry với file nhỏ hơn

#### 8.2 Test Invalid File Type
```bash
# Try upload .exe file (should reject)
curl -X POST http://165.99.59.47/api/documents/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@program.exe"

# Kết quả mong đợi: Error "Invalid file type"
```

#### 8.3 Test Unauthorized Access
```bash
# Try access protected endpoint without token
curl -X GET http://165.99.59.47/api/users/stats

# Kết quả mong đợi: 401 Unauthorized
```

---

### 9. Test Responsive Design

**Kiểm tra trên các device:**
- [ ] Desktop (1920x1080)
- [ ] Laptop (1366x768)
- [ ] Tablet (768x1024)
- [ ] Mobile (375x667)

**Cách test:**
1. Mở Chrome DevTools (F12)
2. Click icon "Toggle device toolbar" (Ctrl+Shift+M)
3. Chọn các device khác nhau
4. Kiểm tra layout không bị vỡ

---

### 10. Test Performance

#### 10.1 Page Load Speed
```bash
# Test with curl và measure time
time curl -s -o /dev/null -w "%{time_total}\n" http://165.99.59.47/

# Kết quả mong đợi: < 2 seconds
```

#### 10.2 API Response Time
```bash
# Test API endpoint speed
time curl -X GET http://165.99.59.47/health

# Kết quả mong đợi: < 200ms
```

#### 10.3 Lighthouse Score
1. Mở Chrome
2. F12 → Lighthouse tab
3. Click "Generate report"
4. Kiểm tra scores:
   - Performance: > 80
   - Accessibility: > 90
   - Best Practices: > 90
   - SEO: > 80

---

## 🔍 Debug Tools

### 1. Check Frontend Logs
```bash
# Trên server
ssh root@165.99.59.47 "docker logs utility_nginx --tail=100"
```

### 2. Check Backend Logs
```bash
ssh root@165.99.59.47 "docker logs utility_backend --tail=100"
```

### 3. Check Network Tab
1. Mở Chrome DevTools (F12)
2. Tab "Network"
3. Refresh page
4. Kiểm tra:
   - Status codes (should be 200, not 404 or 500)
   - Response times
   - Failed requests

### 4. Check Console Errors
1. F12 → Console tab
2. Kiểm tra có error nào không
3. Common errors:
   - CORS errors
   - 404 Not Found
   - JavaScript errors

---

## 📋 Checklist Tổng Hợp

### Frontend Basics
- [ ] Homepage load thành công
- [ ] Login page hiển thị đúng
- [ ] Dashboard accessible
- [ ] Logout function hoạt động
- [ ] Responsive trên mobile

### Document Processing
- [ ] PDF upload thành công
- [ ] PDF to Word conversion
- [ ] PDF to Image conversion
- [ ] PDF merge
- [ ] Word/Excel upload

### Image Processing
- [ ] Image upload
- [ ] Image resize
- [ ] Image crop
- [ ] Image rotate
- [ ] Image format conversion

### OCR Features
- [ ] English OCR
- [ ] Vietnamese OCR
- [ ] Auto-detect language

### Admin Features
- [ ] Admin login
- [ ] User management
- [ ] Statistics display
- [ ] Activity logs

### Error Handling
- [ ] Large file rejection
- [ ] Invalid file type rejection
- [ ] Unauthorized access blocked
- [ ] Error messages user-friendly

### Performance
- [ ] Page load < 2s
- [ ] API response < 500ms
- [ ] No memory leaks
- [ ] Smooth animations

---

## 🚨 Common Issues & Solutions

### Issue 1: Frontend không load (404)
**Nguyên nhân:** Frontend chưa build hoặc Nginx config sai

**Giải pháp:**
```bash
# Rebuild frontend locally
cd frontend
npm run build

# Upload to server
scp -r dist/* root@165.99.59.47:/opt/utility-server/frontend/dist/

# Restart Nginx
ssh root@165.99.59.47 "docker-compose restart nginx"
```

### Issue 2: CORS Error
**Nguyên nhân:** Backend không cho phép frontend domain

**Giải pháp:** Kiểm tra CORS settings trong backend

### Issue 3: API 401 Unauthorized
**Nguyên nhân:** Token expired hoặc không valid

**Giải pháp:** Login lại để get new token

### Issue 4: Slow performance
**Nguyên nhân:** Server overloaded hoặc large files

**Giải pháp:**
```bash
# Check server resources
ssh root@165.99.59.47 "docker stats --no-stream"

# Check memory usage
ssh root@165.99.59.47 "free -h"

# Check disk space
ssh root@165.99.59.47 "df -h"
```

---

## 📞 Support

Nếu gặp vấn đề:
1. Check logs: `docker logs utility_backend`
2. Check Nginx logs: `docker logs utility_nginx`
3. Check console errors in browser (F12)
4. Review this guide for common issues

---

**Last Updated:** 2025-11-21 23:10:00 +07:00
