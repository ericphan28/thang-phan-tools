# Gemini Auto-Logging Service

## Vấn đề

Trước đây phải **manually log** mỗi Gemini API call:
```python
# ❌ Cách cũ - dễ quên log
import google.generativeai as genai

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-2.5-flash")
response = model.generate_content(prompt)

# Developer phải nhớ gọi log_usage() - rất dễ quên!
log_usage(db, "gemini", "gemini-2.5-flash", ...)
```

## Giải pháp: GeminiService

**Auto-log 100% Gemini API calls** bằng wrapper class:

```python
# ✅ Cách mới - tự động log
from app.services.gemini_service import get_gemini_service

gemini = get_gemini_service(db, user_id=1)
response = gemini.generate_content(
    prompt="Write a poem",
    model="gemini-2.5-flash",
    operation="text-generation"
)
# ✅ Đã tự động log vào database!
```

## Features

✅ **Tự động log mọi API call**
- Tokens (input/output)
- Cost (calculated)
- Processing time
- Success/error status
- Request metadata

✅ **Zero config** - chỉ cần import và dùng

✅ **Error handling** - log cả khi fail

✅ **Support streaming** - log sau khi stream xong

## Usage Examples

### 1. Basic text generation

```python
from app.services.gemini_service import get_gemini_service
from app.core.database import get_db

db = next(get_db())
gemini = get_gemini_service(db, user_id=1)

# Simple generation
response = gemini.generate_content(
    prompt="Explain quantum physics",
    model="gemini-2.5-flash",
    operation="explain"
)
print(response.text)
```

### 2. With metadata tracking

```python
gemini = get_gemini_service(db, user_id=1)

response = gemini.generate_content(
    prompt="Generate a document",
    model="gemini-2.5-pro",
    operation="document-generation",
    metadata={
        "document_type": "report",
        "language": "vietnamese",
        "page_count": 5
    }
)
```

### 3. Streaming response

```python
gemini = get_gemini_service(db)

for chunk in gemini.generate_content_stream(
    prompt="Write a long story",
    model="gemini-2.5-flash",
    operation="story-generation"
):
    print(chunk.text, end="")
# ✅ Log được ghi sau khi stream xong
```

### 4. Using in FastAPI endpoints

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.gemini_service import get_gemini_service

router = APIRouter()

@router.post("/generate")
async def generate_text(
    prompt: str,
    db: Session = Depends(get_db)
):
    gemini = get_gemini_service(db)
    
    response = gemini.generate_content(
        prompt=prompt,
        model="gemini-2.5-flash",
        operation="api-generate"
    )
    
    return {"text": response.text}
    # ✅ Usage đã được log!
```

### 5. OCR với Gemini Vision

```python
gemini = get_gemini_service(db, user_id=1)

response = gemini.generate_content(
    prompt=["Extract text from this image", image_data],
    model="gemini-2.5-flash",
    operation="ocr",
    metadata={"file_name": "invoice.pdf", "page": 1}
)
```

## Models Available

| Model | Input Cost | Output Cost | Use Case |
|-------|------------|-------------|----------|
| gemini-2.5-flash | $0.50/1M | $2.00/1M | Fast, general |
| gemini-2.5-pro | $1.25/1M | $5.00/1M | Complex reasoning |
| gemini-2.0-flash-exp | $0.075/1M | $0.30/1M | Experimental |

## Logging Details

Mọi call được log vào table `ai_usage_logs` với:

```sql
- provider: "gemini"
- model: "gemini-2.5-flash"
- operation: "text-generation"
- input_tokens: 150
- output_tokens: 500
- total_tokens: 650
- total_cost: 0.0 (free tier) hoặc calculated cost (paid)
- processing_time_ms: 1234.56
- status: "success" hoặc "error"
- error_message: null hoặc error details
- request_metadata: JSON metadata
- created_at: timestamp
```

## Free Tier Tracking

Service tự động check quota:
- **1,500 requests/day** (dùng chung cho tất cả models)
- Auto-log mỗi request
- Dashboard shows: "1,499 / 1,500 còn lại"
- Warning khi > 90% quota (1,350+ requests)

## Migration Guide

### Old Code (manual logging)
```python
# ❌ Cũ
import google.generativeai as genai

genai.configure(api_key=settings.GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")
response = model.generate_content(prompt)

# Phải nhớ log
log_usage(db, "gemini", "gemini-2.5-flash", ...)
```

### New Code (auto-logging)
```python
# ✅ Mới
from app.services.gemini_service import get_gemini_service

gemini = get_gemini_service(db)
response = gemini.generate_content(prompt, model="gemini-2.5-flash")
# Tự động log!
```

## Best Practices

1. ✅ **Luôn dùng GeminiService** thay vì SDK trực tiếp
2. ✅ **Truyền operation name** rõ ràng (e.g., "ocr", "text-to-word")
3. ✅ **Thêm metadata** để tracking chi tiết
4. ✅ **Truyền user_id** nếu biết user
5. ⚠️ **Không dùng cho token counting** (free operation)

## Implementation Checklist

Để đảm bảo 100% Gemini calls được log:

- [ ] Replace tất cả `genai.GenerativeModel()` → `get_gemini_service()`
- [ ] Update tất cả endpoints sử dụng Gemini
- [ ] Add operation names cho mỗi use case
- [ ] Test dashboard quota tracking
- [ ] Document operation names trong code

## Next Steps

1. **Migrate existing code**: Tìm tất cả chỗ dùng `genai.` và thay bằng `GeminiService`
2. **Add to all new features**: Mọi feature mới phải dùng `GeminiService`
3. **Monitor dashboard**: Check "Provider Live Status" để track quota
4. **Set alerts**: Warning khi quota > 90%
