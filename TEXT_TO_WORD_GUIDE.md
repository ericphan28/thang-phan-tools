# ✨ AI TEXT TO WORD - MHTML FORMAT

## 🎯 Tổng Quan

Tính năng mới cho phép chuyển đổi **văn bản thuần (plain text)** thành **tài liệu Word đẹp mắt** với định dạng chuyên nghiệp, sử dụng AI (Gemini/Claude) để phân tích cấu trúc và MHTML format để tạo file `.doc`.

## 🌟 Điểm Nổi Bật

### ✅ **Smart AI Formatting**
- AI tự động nhận diện tiêu đề (H1, H2, H3)
- Tách sections và subsections
- Tạo danh sách bullets tự động
- Highlight tên người, địa điểm, thuật ngữ quan trọng
- Tạo info boxes cho thông tin quan trọng
- Tạo highlight boxes cho kết luận

### ✅ **Multi AI Provider**
- **Gemini** (Google): Nhanh, tiết kiệm, tốt cho tiếng Việt
- **Claude** (Anthropic): Chất lượng cao, reasoning tốt

### ✅ **Professional Output**
- Format: `.doc` (MHTML)
- Page size: A4 (21cm × 29.7cm)
- Font: Times New Roman 13pt
- Thụt đầu dòng: 1cm (chuẩn văn bản Việt Nam)
- Màu sắc và borders đẹp mắt
- Tương thích: Word 2000+, Google Docs, LibreOffice

### ✅ **AI Admin Integration**
- Tự động lấy API keys từ hệ thống AI Admin
- Budget checking trước khi xử lý
- Usage tracking và cost calculation
- Log chi tiết cho audit

## 🏗️ Kiến Trúc

```
┌─────────────┐
│   User      │
│  Input Text │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────┐
│   Backend API               │
│  /text-to-word-smart        │
└──────┬──────────────────────┘
       │
       ▼
┌─────────────────────────────┐
│  AI Admin System            │
│  • Get API Key              │
│  • Check Budget             │
└──────┬──────────────────────┘
       │
       ▼
┌─────────────────────────────┐
│  AI Provider                │
│  • Gemini: Analyze text     │
│  • Claude: Structure data   │
└──────┬──────────────────────┘
       │
       ▼
┌─────────────────────────────┐
│  MHTML Generator            │
│  • Generate HTML            │
│  • Add Word metadata        │
│  • CSS styling              │
└──────┬──────────────────────┘
       │
       ▼
┌─────────────────────────────┐
│   .doc File                 │
│   Download to user          │
└─────────────────────────────┘
```

## 📁 File Structure

```
backend/
├── app/services/document_service.py
│   ├── text_to_word_mhtml()          # Main function
│   ├── _format_text_with_gemini()    # Gemini integration
│   ├── _format_text_with_claude()    # Claude integration
│   ├── _build_format_prompt()        # Prompt engineering
│   ├── _generate_mhtml()             # MHTML generation
│   └── _escape_html()                # HTML sanitization
│
└── app/api/v1/endpoints/documents.py
    ├── POST /text-to-word-smart      # Main endpoint
    └── GET  /ai-providers            # List providers

frontend/
└── src/pages/TextToWordPage.tsx      # React UI
```

## 🔧 Cách Sử Dụng

### 1️⃣ **Setup API Keys (One-time)**

Vào trang **AI Keys Management** và thêm API keys:

```bash
# Gemini API Key
Provider: gemini
Key Name: "Gemini Primary"
API Key: AIzaSy...
Is Primary: ✅
Is Active: ✅

# Claude API Key (optional)
Provider: claude
Key Name: "Claude Sonnet"
API Key: sk-ant-...
Is Primary: ✅
Is Active: ✅
```

### 2️⃣ **Sử dụng UI**

1. Mở trang **AI Text→Word** từ sidebar
2. Nhập văn bản (tối thiểu 10 ký tự)
3. Chọn AI Provider (Gemini/Claude)
4. Chọn Model (optional)
5. Chọn ngôn ngữ (vi/en/zh/ja...)
6. Click **"Tạo Word Document"**
7. File `.doc` tự động download

### 3️⃣ **Sử dụng API**

#### **Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/documents/text-to-word-smart" \
  -F "text=Báo cáo dự án ABC..." \
  -F "provider=gemini" \
  -F "model=gemini-2.5-flash" \
  -F "language=vi" \
  --output document.doc
```

#### **Response Headers:**
```
X-Technology-Engine: gemini
X-Technology-Name: Gemini AI
X-Technology-Model: gemini-2.5-flash
X-Technology-Quality: 8/10
X-Input-Tokens: 523
X-Output-Tokens: 1847
X-Processing-Time-Ms: 3421
```

### 4️⃣ **Python Script**

```bash
python test_text_to_word.py
```

Kết quả:
- `output_gemini.doc` - Gemini generated
- `output_claude.doc` - Claude generated (if enabled)

## 🎨 AI Auto-Detection

### **Input Example:**
```
Báo cáo dự án Website

Giới thiệu: Dự án được khởi động...

Các tính năng chính:
- Tìm kiếm thông minh
- Thanh toán đa phương thức
- Quản lý đơn hàng realtime

Tiến độ: Giai đoạn 1 hoàn thành 100%...

Kết luận: Dự án đi đúng tiến độ.
```

### **AI Output:**
```json
{
  "title": "Báo cáo dự án Website",
  "sections": [
    {
      "heading": "Giới thiệu",
      "level": 1,
      "content": [
        {
          "type": "paragraph",
          "text": "Dự án được khởi động...",
          "highlights": ["Dự án"]
        }
      ]
    },
    {
      "heading": "Các tính năng chính",
      "level": 1,
      "content": [
        {
          "type": "list",
          "items": [
            "Tìm kiếm thông minh",
            "Thanh toán đa phương thức",
            "Quản lý đơn hàng realtime"
          ]
        }
      ]
    },
    {
      "heading": "Kết luận",
      "level": 1,
      "content": [
        {
          "type": "highlight_box",
          "title": "KẾT LUẬN",
          "text": "Dự án đi đúng tiến độ."
        }
      ]
    }
  ]
}
```

## 📊 Technology Comparison

### **MHTML (This Feature) vs python-docx**

| Feature | MHTML | python-docx |
|---------|-------|-------------|
| **Complexity** | ⭐⭐ Simple | ⭐⭐⭐⭐ Complex |
| **File Format** | .doc (old) | .docx (modern) |
| **Quality** | 8/10 | 9.5/10 |
| **Client-side** | ✅ Yes | ❌ No |
| **Speed** | ⚡ Fast | 🐢 Medium |
| **Dependencies** | None | python-docx |
| **AI Integration** | ✅ Easy | ⚠️ Medium |
| **Tables** | ⚠️ HTML | ✅ Native |
| **Images** | Base64 | ✅ Native |

### **When to use MHTML?**
- ✅ Simple text documents
- ✅ Fast generation needed
- ✅ Client-side export
- ✅ AI-powered formatting

### **When to use python-docx?**
- ✅ Complex layouts
- ✅ Native tables/charts
- ✅ Images from URLs
- ✅ Track changes/comments

## 💰 Cost Estimation

### **Gemini (Recommended)**
```
Model: gemini-2.5-flash
Input:  $0.50 / 1M tokens
Output: $2.00 / 1M tokens

Average document (2000 words):
• Input tokens:  ~500
• Output tokens: ~1500
• Total cost: $0.003 (0.003 USD)
```

### **Claude**
```
Model: claude-3-5-sonnet
Input:  $3.00 / 1M tokens
Output: $15.00 / 1M tokens

Average document (2000 words):
• Input tokens:  ~500
• Output tokens: ~1500
• Total cost: $0.024 (0.024 USD)
```

**💡 Tip:** Gemini 8x rẻ hơn Claude cho use case này!

## 🔍 Debugging

### **Check AI Keys:**
```bash
curl http://localhost:8000/api/v1/ai-admin/keys | jq
```

### **Check Budget:**
```bash
curl http://localhost:8000/api/v1/ai-admin/balance/gemini | jq
```

### **View Logs:**
```bash
curl http://localhost:8000/api/v1/ai-admin/usage-logs?provider=gemini | jq
```

## 🚀 Next Steps

### **Possible Enhancements:**
1. ✨ Add table support (auto-detect tabular data)
2. 🖼️ Support images (Base64 embed)
3. 📊 Generate charts from data
4. 🎨 Custom templates (corporate, academic, etc.)
5. 🌐 Support more languages (Thai, Indonesian, etc.)
6. 💾 Save templates to database
7. 📱 Mobile app integration

## 📝 Example Use Cases

### 1. **Meeting Minutes**
```
Input: Raw notes from meeting
Output: Formatted document with sections, attendees, action items
```

### 2. **Project Reports**
```
Input: Project progress text
Output: Professional report with intro, milestones, conclusion
```

### 3. **Content Articles**
```
Input: Blog post or article text
Output: Formatted document with headings, quotes, highlights
```

### 4. **Resume/CV**
```
Input: Career information
Output: Structured resume with sections
```

## 🎯 Best Practices

1. **Chuẩn bị text tốt:**
   - Dùng line breaks để tách sections
   - Dùng `-` hoặc `•` cho lists
   - Đặt tiêu đề rõ ràng

2. **Chọn provider phù hợp:**
   - Gemini: Văn bản đơn giản, tiếng Việt
   - Claude: Nội dung phức tạp, cần reasoning

3. **Monitor costs:**
   - Set monthly limits trong AI Admin
   - Review usage logs thường xuyên

4. **Test output:**
   - Kiểm tra file trong Word trước khi gửi
   - Adjust text nếu format không đúng ý

## 📞 Support

- **Documentation:** [AI_CONTEXT.md](./AI_CONTEXT.md)
- **API Docs:** http://localhost:8000/docs
- **Test Script:** `python test_text_to_word.py`

---

**Made with ❤️ using Claude AI's MHTML technique**
