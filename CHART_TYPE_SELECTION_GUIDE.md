# 📊 HƯỚNG DẪN CHỌN LOẠI BIỂU ĐỒ TỐI ƯU

## 🤖 AI Tự Động Chọn - Bạn Không Cần Lo!

AI (Gemini/Claude) **TỰ ĐỘNG phân tích** dữ liệu và chọn loại biểu đồ phù hợp nhất dựa trên:
- Bản chất dữ liệu (so sánh, xu hướng, tỷ lệ...)
- Số lượng điểm dữ liệu
- Mối quan hệ giữa các biến

---

## 📐 QUY TẮC CHỌN BIỂU ĐỒ

### 1. 📊 **BAR CHART (Biểu đồ cột)** - `"bar"`

**Khi nào dùng:**
- So sánh giữa các mục riêng biệt
- Dữ liệu phân loại (categories)
- Nhiều items cần so sánh với nhau

**Ví dụ phù hợp:**
```
Doanh thu các chi nhánh:
- Hà Nội: 500 triệu
- TP.HCM: 650 triệu
- Đà Nẵng: 320 triệu
- Cần Thơ: 180 triệu
→ AI sẽ tạo: BAR CHART
```

```
Sản lượng bán hàng theo sản phẩm:
- Sản phẩm A: 1200 đơn vị
- Sản phẩm B: 980 đơn vị
- Sản phẩm C: 1500 đơn vị
→ AI sẽ tạo: BAR CHART
```

**Tại sao?** Dễ so sánh chiều cao các cột → thấy rõ item nào cao/thấp nhất

---

### 2. 📈 **LINE CHART (Biểu đồ đường)** - `"line"`

**Khi nào dùng:**
- Dữ liệu theo thời gian (time series)
- Hiển thị xu hướng tăng/giảm
- Dữ liệu liên tục

**Ví dụ phù hợp:**
```
Tăng trưởng doanh thu 2024:
- Tháng 1: 100 triệu
- Tháng 2: 115 triệu
- Tháng 3: 130 triệu
- Tháng 4: 125 triệu
- Tháng 5: 145 triệu
- Tháng 6: 160 triệu
→ AI sẽ tạo: LINE CHART
```

```
Nhiệt độ trung bình các quý:
Q1 2024: 25°C
Q2 2024: 28°C
Q3 2024: 30°C
Q4 2024: 26°C
→ AI sẽ tạo: LINE CHART
```

**Tại sao?** Đường nối liền → thấy rõ xu hướng tăng/giảm theo thời gian

---

### 3. 🥧 **PIE CHART (Biểu đồ tròn)** - `"pie"`

**Khi nào dùng:**
- Hiển thị tỷ lệ phần trăm
- Tổng = 100%
- Ít mục (3-6 mục tối đa)
- Cơ cấu, thành phần

**Ví dụ phù hợp:**
```
Cơ cấu doanh thu theo kênh bán:
- Online: 45%
- Cửa hàng: 35%
- Đại lý: 20%
→ AI sẽ tạo: PIE CHART
```

```
Thị phần smartphone Việt Nam:
- Samsung: 40%
- Apple: 25%
- Oppo: 20%
- Xiaomi: 15%
→ AI sẽ tạo: PIE CHART
```

**Tại sao?** Hình tròn → thấy rõ tỷ lệ phần trăm của từng phần so với tổng thể

**⚠️ LƯU Ý:** AI chỉ tạo pie chart khi:
- Các giá trị là % HOẶC tổng ≈ 100
- Không quá nhiều mục (>6 mục sẽ rối)

---

### 4. 🔵 **SCATTER PLOT (Biểu đồ phân tán)** - `"scatter"`

**Khi nào dùng:**
- Mối quan hệ giữa 2 biến số
- Tìm correlation (tương quan)
- Dữ liệu có 2 trục (X và Y)

**Ví dụ phù hợp:**
```
Mối quan hệ chi tiêu quảng cáo & doanh thu:
- Chi 10 triệu → Doanh thu 50 triệu
- Chi 20 triệu → Doanh thu 85 triệu
- Chi 30 triệu → Doanh thu 120 triệu
- Chi 40 triệu → Doanh thu 150 triệu
→ AI sẽ tạo: SCATTER PLOT
```

```
Tuổi nhân viên vs Năng suất:
- 25 tuổi: 80 điểm
- 30 tuổi: 95 điểm
- 35 tuổi: 92 điểm
- 40 tuổi: 88 điểm
→ AI sẽ tạo: SCATTER PLOT
```

**Tại sao?** Các điểm rải rác → thấy rõ mối quan hệ giữa 2 biến

---

## 🎯 BẢNG QUYẾT ĐỊNH NHANH

| **Câu hỏi dữ liệu** | **Loại biểu đồ** | **Ví dụ** |
|-------------------|----------------|---------|
| So sánh giữa các mục? | 📊 BAR | Doanh thu theo chi nhánh |
| Thay đổi theo thời gian? | 📈 LINE | Tăng trưởng theo tháng |
| Tỷ lệ % của từng phần? | 🥧 PIE | Thị phần, cơ cấu |
| Quan hệ 2 biến số? | 🔵 SCATTER | Chi phí vs Hiệu quả |

---

## 💡 LOGIC AI CHỌN BIỂU ĐỒ

### Bước 1: Phát hiện dữ liệu số
AI quét text tìm:
- Số + đơn vị: `150 triệu`, `45%`, `1200 đơn vị`
- Danh sách có số liệu
- So sánh có giá trị cụ thể

### Bước 2: Phân tích cấu trúc
- **Có time keywords** (tháng, quý, năm, ngày) → LINE CHART
- **Có % và tổng ≈ 100** → PIE CHART
- **Có 2 biến độc lập** → SCATTER PLOT
- **Mặc định: So sánh items** → BAR CHART

### Bước 3: Kiểm tra số lượng
- **Pie chart**: Chỉ khi 3-6 mục (nhiều hơn sẽ rối)
- **Line chart**: Ít nhất 3 điểm (để thấy xu hướng)
- **Bar chart**: Bất kỳ số lượng nào

### Bước 4: Tối ưu hóa
AI tự động:
- Chọn màu phù hợp
- Đặt label rõ ràng
- Tạo description cho biểu đồ
- Đặt biểu đồ ở vị trí hợp lý trong document

---

## ✅ VÍ DỤ THỰC TẾ

### Ví dụ 1: AI tạo 2 biểu đồ từ 1 đoạn text

**Input:**
```
Báo cáo kinh doanh Q4/2024

Doanh thu các tháng:
- Tháng 10: 500 triệu
- Tháng 11: 650 triệu
- Tháng 12: 720 triệu

Phân tích cơ cấu doanh thu:
- Sản phẩm A chiếm 45%
- Sản phẩm B chiếm 30%
- Sản phẩm C chiếm 25%
```

**Output AI tự tạo:**
1. 📈 **LINE CHART**: Doanh thu theo tháng (vì có time series)
2. 🥧 **PIE CHART**: Cơ cấu sản phẩm (vì có % và tổng = 100%)

---

### Ví dụ 2: AI KHÔNG tạo biểu đồ

**Input:**
```
Python là ngôn ngữ lập trình phổ biến.

Ưu điểm:
- Dễ học
- Cộng đồng lớn
- Nhiều thư viện

Kết luận: Python rất tốt cho người mới bắt đầu.
```

**Output:** Chỉ có văn bản định dạng đẹp, KHÔNG có biểu đồ

**Tại sao?** Không có số liệu cụ thể → không cần biểu đồ

---

## 🎨 TUỲ CHỈNH (Nâng cao)

Nếu muốn kiểm soát màu sắc hoặc style, edit file:
```
backend/app/services/document_service.py
→ Method: _create_chart()
```

**Tùy chỉnh màu:**
```python
# Default colors
colors = data.get("colors", [
    "#3498db",  # Blue
    "#2ecc71",  # Green  
    "#e74c3c",  # Red
    "#f39c12",  # Orange
    "#9b59b6"   # Purple
])
```

**Tùy chỉnh resolution:**
```python
plt.savefig(img_stream, format='png', dpi=200)  # 150-300 recommended
```

---

## 🚀 CÁCH SỬ DỤNG

### Giao diện Web
1. Mở: http://localhost:5174/data-visualization
2. Nhập text có số liệu
3. Click "Tạo Biểu đồ"
4. AI tự động:
   - Phân tích dữ liệu
   - Chọn loại biểu đồ phù hợp
   - Tạo biểu đồ đẹp
   - Embed vào Word document

### API Endpoint
```bash
POST /api/v1/documents/generate-visualization
FormData:
  - text_input: "Doanh thu Q1: 100, Q2: 150, Q3: 200"
  - language: "vi"
  - provider: "gemini"

Response: .docx file với biểu đồ tự động
```

---

## 📚 TÓM TẮT

✅ **Bạn KHÔNG CẦN chọn** - AI làm tự động  
✅ **Chỉ cần nhập dữ liệu** - AI phân tích và chọn biểu đồ tối ưu  
✅ **4 loại biểu đồ** được hỗ trợ: bar, line, pie, scatter  
✅ **Logic thông minh** dựa trên bản chất dữ liệu  
✅ **Chất lượng cao** - matplotlib @ 200 DPI  

---

**💡 Mẹo pro:** Cung cấp dữ liệu rõ ràng → AI chọn biểu đồ chính xác hơn!

**🔥 Technology:** Gemini AI + matplotlib + python-docx  
**📅 Cập nhật:** 23/12/2024
