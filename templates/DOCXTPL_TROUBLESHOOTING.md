# 🔧 DOCXTPL TROUBLESHOOTING & BEST PRACTICES

## ❌ CÁC LỖI THƯỜNG GẶP & CÁCH SỬA

### Lỗi 1: Template not found

**Triệu chứng:**
```
FileNotFoundError: [Errno 2] No such file or directory: 'mau_2c_template_docxtpl.docx'
```

**Nguyên nhân:**
- File template không tồn tại
- Đường dẫn sai
- Chạy script ở thư mục khác

**Giải pháp:**
```python
from pathlib import Path

# Check if template exists
template_path = Path("mau_2c_template_docxtpl.docx")
if not template_path.exists():
    print(f"❌ Template không tồn tại: {template_path.absolute()}")
    print(f"   Đang ở thư mục: {Path.cwd()}")
    print(f"   Vui lòng chạy: python create_template_docxtpl.py")
    exit(1)

# Load template
doc = DocxTemplate(template_path)
```

---

### Lỗi 2: TemplateSyntaxError

**Triệu chứng:**
```
jinja2.exceptions.TemplateSyntaxError: expected token 'end of print statement', got ':'
```

**Nguyên nhân:**
- Syntax Jinja2 sai
- Thiếu `%}` hoặc `}}`
- Dùng `:` trong variable name

**Ví dụ SAI:**
```jinja2
{{ dia:chi }}  ❌ Có dấu :
{% for item in list  ❌ Thiếu %}
{{ name }  ❌ Thiếu }
```

**Ví dụ ĐÚNG:**
```jinja2
{{ dia_chi }}  ✅
{% for item in list %}  ✅
{{ name }}  ✅
```

**Giải pháp:**
1. Kiểm tra tất cả tags có đầy đủ `{{` `}}` và `{%` `%}`
2. Không dùng `:` trong variable name, thay bằng `_`
3. Test từng phần nhỏ

---

### Lỗi 3: UndefinedError - Variable not found

**Triệu chứng:**
```
jinja2.exceptions.UndefinedError: 'ho_ten' is undefined
```

**Nguyên nhân:**
- JSON thiếu field
- Tên variable không match
- Case-sensitive

**Template:**
```jinja2
{{ ho_ten }}  ← Tìm "ho_ten"
```

**JSON SAI:**
```json
{
  "hoTen": "Nguyễn Văn An"  ❌ Case khác
}
```

**JSON ĐÚNG:**
```json
{
  "ho_ten": "Nguyễn Văn An"  ✅
}
```

**Giải pháp:**

```python
from docxtpl import DocxTemplate

doc = DocxTemplate('template.docx')

# Option 1: Use default filter trong template
# {{ ho_ten|default("Chưa cập nhật") }}

# Option 2: Check missing variables
context = {"tinh": "Bình Dương"}  # Thiếu "ho_ten"

# Get undefined variables
doc.render(context)
undefined = doc.get_undeclared_template_variables()
if undefined:
    print(f"❌ Missing variables: {undefined}")
    # Add default values
    for var in undefined:
        context[var] = ""
```

---

### Lỗi 4: Table structure corrupted

**Triệu chứng:**
- Bảng bị vỡ format
- Cells bị merge sai
- Borders mất

**Nguyên nhân:**
- Đặt tags Jinja2 sai vị trí
- Không dùng `{%tr` tag
- Edit trực tiếp XML

**SAI:**
```jinja2
{% for item in list %}
Cell 1 | Cell 2 | Cell 3
{% endfor %}
```

**ĐÚNG:**
```jinja2
{%tr for item in list %}
Cell 1 | Cell 2 | Cell 3
{%tr endfor %}
```

**Giải pháp:**
- Dùng `{%tr` cho table row
- Dùng `{%tc` cho table cell
- Dùng `{%p` cho paragraph
- Không edit XML trực tiếp

---

### Lỗi 5: Vietnamese characters broken

**Triệu chứng:**
```
Output: Nguyá»n VÄn An  ❌
Should: Nguyễn Văn An  ✅
```

**Nguyên nhân:**
- JSON không dùng UTF-8 encoding
- Python file không UTF-8

**Giải pháp:**

```python
import json

# ✅ ĐÚNG: Specify encoding
with open('data.json', encoding='utf-8') as f:
    context = json.load(f)

# ❌ SAI: No encoding
with open('data.json') as f:  # Default = system encoding
    context = json.load(f)
```

**Lưu JSON với UTF-8:**
```python
import json

data = {"ho_ten": "Nguyễn Văn An"}

with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
```

---

### Lỗi 6: Empty array causes missing table rows

**Triệu chứng:**
- Bảng không có data
- Hàng bị trống

**Template:**
```jinja2
{%tr for edu in dao_tao %}
{{ edu.ten_truong }} | {{ edu.nganh_hoc }}
{%tr endfor %}
```

**JSON:**
```json
{
  "dao_tao": []  ← Array rỗng!
}
```

**Output:** Bảng không có hàng data!

**Giải pháp:**

**Option 1: Check before render**
```python
context = json.load(f)

# Add default empty row if array is empty
if not context.get('dao_tao'):
    context['dao_tao'] = [{
        "ten_truong": "",
        "nganh_hoc": "",
        "thoi_gian": "",
        "hinh_thuc": "",
        "van_bang": ""
    }]

doc.render(context)
```

**Option 2: Use conditional trong template**
```jinja2
{%tr if dao_tao %}
  {%tr for edu in dao_tao %}
  {{ edu.ten_truong }} | {{ edu.nganh_hoc }}
  {%tr endfor %}
{%tr else %}
  {%tr %}
  Chưa có dữ liệu | | | |
  {%tr %}
{%tr endif %}
```

---

### Lỗi 7: Special characters cause XML error

**Triệu chứng:**
```
XMLSyntaxError: Entity 'nbsp' not defined
```

**Nguyên nhân:**
- Dùng `<`, `>`, `&` trong data
- HTML entities trong text

**JSON SAI:**
```json
{
  "mo_ta": "Điểm >= 8"  ❌ Có ký tự >
}
```

**Giải pháp:**

**Option 1: Use escape filter**
```jinja2
{{ mo_ta|e }}
```

**Option 2: Enable autoescape**
```python
doc.render(context, autoescape=True)
```

**Option 3: Use Listing class**
```python
from docxtpl import Listing

context = {
    "mo_ta": Listing("Điểm >= 8 và < 10")  # Auto-escape
}
```

---

### Lỗi 8: Line breaks not working

**Triệu chứng:**
```
Output: Dòng 1\nDòng 2  ← \n hiển thị literal
```

**Nguyên nhân:**
- `\n` không được interpret

**Giải pháp:**

**Option 1: Use RichText**
```python
from docxtpl import RichText

rt = RichText("Dòng 1\nDòng 2\nDòng 3")
context = {"text_with_newlines": rt}
```

**Template:**
```jinja2
{{r text_with_newlines }}  ← Note the 'r'
```

**Option 2: Use paragraph tags**
```jinja2
{%p for line in lines %}
{{ line }}
{%p endfor %}
```

**JSON:**
```json
{
  "lines": ["Dòng 1", "Dòng 2", "Dòng 3"]
}
```

---

### Lỗi 9: Image not displaying

**Triệu chứng:**
- Image path có trong JSON nhưng không hiện

**Nguyên nhân:**
- Không dùng InlineImage class
- Path sai

**SAI:**
```python
context = {
    "photo": "photo.jpg"  ❌ String không work
}
```

**ĐÚNG:**
```python
from docxtpl import InlineImage
from docx.shared import Mm

doc = DocxTemplate('template.docx')
image = InlineImage(doc, 'photo.jpg', width=Mm(30))

context = {
    "photo": image  ✅ InlineImage object
}
```

**Template:**
```jinja2
{{ photo }}  ← Not {{r photo }}
```

---

### Lỗi 10: Multiple rendering issues

**Triệu chứng:**
- Lần render thứ 2 báo lỗi
- Data từ lần trước còn sót lại

**Nguyên nhân:**
- DocxTemplate object được reuse

**SAI:**
```python
doc = DocxTemplate('template.docx')

# Render multiple times
for person in people:
    doc.render(person)  ❌ Conflict!
    doc.save(f'{person["ho_ten"]}.docx')
```

**ĐÚNG:**
```python
for person in people:
    # Create NEW template object each time
    doc = DocxTemplate('template.docx')  ✅
    doc.render(person)
    doc.save(f'{person["ho_ten"]}.docx')
```

---

## ✅ BEST PRACTICES

### 1. Template Organization

**Structure:**
```
project/
├── templates/
│   ├── mau_2c_template_docxtpl.docx  ← Main template
│   ├── header_template.docx          ← Sub-template
│   └── footer_template.docx
├── data/
│   ├── mau_2c_DATA_FULL.json        ← Sample data
│   └── schema.json                   ← JSON schema
├── scripts/
│   ├── create_template.py
│   ├── generate_document.py
│   └── batch_generate.py
└── output/
    └── generated_documents/
```

---

### 2. JSON Data Validation

**Use JSON Schema:**
```python
import json
import jsonschema

# Define schema
schema = {
    "type": "object",
    "required": ["ho_ten", "tinh", "ngay", "thang", "nam"],
    "properties": {
        "ho_ten": {"type": "string", "minLength": 1},
        "tinh": {"type": "string"},
        "ngay": {"type": "string", "pattern": "^[0-9]{1,2}$"},
        "dao_tao": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["ten_truong", "nganh_hoc"]
            }
        }
    }
}

# Validate before render
try:
    jsonschema.validate(context, schema)
    doc.render(context)
except jsonschema.ValidationError as e:
    print(f"❌ Invalid data: {e.message}")
```

---

### 3. Error Handling

```python
from docxtpl import DocxTemplate
import json
from pathlib import Path

def generate_document(template_path, data_path, output_path):
    """
    Generate document with proper error handling
    """
    try:
        # 1. Check template exists
        if not Path(template_path).exists():
            raise FileNotFoundError(f"Template not found: {template_path}")
        
        # 2. Load and validate JSON
        with open(data_path, encoding='utf-8') as f:
            context = json.load(f)
        
        # 3. Check required fields
        required = ['ho_ten', 'tinh', 'ngay', 'thang', 'nam']
        missing = [f for f in required if f not in context]
        if missing:
            raise ValueError(f"Missing required fields: {missing}")
        
        # 4. Load template
        doc = DocxTemplate(template_path)
        
        # 5. Get undeclared variables
        undefined = doc.get_undeclared_template_variables(context)
        if undefined:
            print(f"⚠️ Warning: Undefined variables: {undefined}")
            # Add defaults
            for var in undefined:
                context[var] = ""
        
        # 6. Render
        doc.render(context)
        
        # 7. Save
        doc.save(output_path)
        
        print(f"✅ Success: {output_path}")
        return True
        
    except FileNotFoundError as e:
        print(f"❌ File Error: {e}")
    except json.JSONDecodeError as e:
        print(f"❌ JSON Error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    return False
```

---

### 4. Performance Optimization

**For batch processing:**

```python
from docxtpl import DocxTemplate
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

def generate_one(person_data, template_path, output_dir):
    """Generate document for one person"""
    try:
        doc = DocxTemplate(template_path)
        doc.render(person_data)
        
        filename = f"{person_data['ho_ten'].replace(' ', '_')}.docx"
        output_path = Path(output_dir) / filename
        
        doc.save(str(output_path))
        return True, filename
    except Exception as e:
        return False, str(e)

def batch_generate_parallel(template_path, data_list, output_dir, max_workers=4):
    """
    Generate multiple documents in parallel
    """
    Path(output_dir).mkdir(exist_ok=True)
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for person in data_list:
            future = executor.submit(
                generate_one, person, template_path, output_dir
            )
            futures.append((future, person.get('ho_ten', 'Unknown')))
        
        # Wait and collect results
        for future, name in futures:
            success, result = future.result()
            if success:
                print(f"✅ {name}: {result}")
            else:
                print(f"❌ {name}: {result}")

# Usage
with open('danh_sach.json', encoding='utf-8') as f:
    all_people = json.load(f)

batch_generate_parallel(
    'mau_2c_template_docxtpl.docx',
    all_people,
    'output',
    max_workers=4
)
```

**Performance:**
- Sequential: 100 docs = 60 seconds
- Parallel (4 workers): 100 docs = 20 seconds

---

### 5. Template Versioning

```python
from docxtpl import DocxTemplate
from datetime import datetime

class TemplateManager:
    """Manage template versions"""
    
    def __init__(self, template_dir='templates'):
        self.template_dir = Path(template_dir)
    
    def get_template(self, name, version=None):
        """Get specific template version"""
        if version:
            template_path = self.template_dir / f"{name}_v{version}.docx"
        else:
            template_path = self.template_dir / f"{name}_latest.docx"
        
        if not template_path.exists():
            raise FileNotFoundError(f"Template not found: {template_path}")
        
        return DocxTemplate(template_path)
    
    def save_version(self, name, template_obj):
        """Save new template version"""
        version = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = self.template_dir / f"{name}_v{version}.docx"
        template_obj.save(output_path)
        
        # Also save as latest
        latest_path = self.template_dir / f"{name}_latest.docx"
        template_obj.save(latest_path)
        
        return version

# Usage
tm = TemplateManager()
doc = tm.get_template('mau_2c')  # Gets mau_2c_latest.docx
# or
doc = tm.get_template('mau_2c', version='20251126')  # Gets specific version
```

---

### 6. Logging

```python
import logging
from docxtpl import DocxTemplate

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('docxtpl.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def generate_with_logging(template_path, data, output_path):
    """Generate document with detailed logging"""
    logger.info(f"Starting generation: {output_path}")
    logger.info(f"Template: {template_path}")
    logger.info(f"Data keys: {list(data.keys())}")
    
    try:
        doc = DocxTemplate(template_path)
        logger.debug("Template loaded successfully")
        
        doc.render(data)
        logger.debug("Template rendered successfully")
        
        doc.save(output_path)
        logger.info(f"✅ Document saved: {output_path}")
        
        file_size = Path(output_path).stat().st_size
        logger.info(f"File size: {file_size:,} bytes")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Generation failed: {e}", exc_info=True)
        return False
```

---

### 7. Testing

```python
import unittest
from docxtpl import DocxTemplate
import json
from pathlib import Path

class TestDocxtpl(unittest.TestCase):
    
    def setUp(self):
        """Setup test fixtures"""
        self.template_path = 'templates/mau_2c_template_docxtpl.docx'
        self.test_data = {
            "ho_ten": "Test User",
            "tinh": "Test Province",
            "ngay": "01",
            "thang": "01",
            "nam": "2000",
            "dao_tao": [],
            "cong_tac": [],
            "gia_dinh": [],
            "gia_dinh_vo_chong": [],
            "luong": []
        }
    
    def test_template_exists(self):
        """Test template file exists"""
        self.assertTrue(Path(self.template_path).exists())
    
    def test_render_with_minimal_data(self):
        """Test rendering with minimal required data"""
        doc = DocxTemplate(self.template_path)
        doc.render(self.test_data)
        
        output_path = 'test_output.docx'
        doc.save(output_path)
        
        self.assertTrue(Path(output_path).exists())
        Path(output_path).unlink()  # Cleanup
    
    def test_undefined_variables(self):
        """Test undefined variable detection"""
        doc = DocxTemplate(self.template_path)
        incomplete_data = {"ho_ten": "Test"}
        
        doc.render(incomplete_data)
        undefined = doc.get_undeclared_template_variables(incomplete_data)
        
        self.assertIsInstance(undefined, set)
    
    def test_vietnamese_characters(self):
        """Test Vietnamese character encoding"""
        doc = DocxTemplate(self.template_path)
        data = self.test_data.copy()
        data['ho_ten'] = "Nguyễn Văn Ăn"
        
        doc.render(data)
        output_path = 'test_vietnamese.docx'
        doc.save(output_path)
        
        self.assertTrue(Path(output_path).exists())
        Path(output_path).unlink()

if __name__ == '__main__':
    unittest.main()
```

---

### 8. Configuration Management

```python
import yaml
from docxtpl import DocxTemplate

class Config:
    """Configuration manager"""
    
    def __init__(self, config_file='config.yaml'):
        with open(config_file, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
    
    def get(self, key, default=None):
        return self.config.get(key, default)

# config.yaml
"""
templates:
  mau_2c: templates/mau_2c_template_docxtpl.docx
  mau_2a: templates/mau_2a_template_docxtpl.docx

output:
  directory: output
  name_pattern: "{ho_ten}_{ngay_ky}_{thang_ky}_{nam_ky}"

validation:
  required_fields:
    - ho_ten
    - tinh
    - ngay
    - thang
    - nam

logging:
  level: INFO
  file: docxtpl.log
"""

# Usage
config = Config()
template_path = config.get('templates')['mau_2c']
doc = DocxTemplate(template_path)
```

---

## 📚 USEFUL RESOURCES

### Official Documentation:
- **docxtpl:** https://docxtpl.readthedocs.io/
- **Jinja2:** https://jinja.palletsprojects.com/
- **python-docx:** https://python-docx.readthedocs.io/

### Examples:
- GitHub: https://github.com/elapouya/python-docx-template/tree/master/tests
- Templates: See `templates/` folder in project

### Community:
- Stack Overflow: [docxtpl tag](https://stackoverflow.com/questions/tagged/docxtpl)
- GitHub Issues: https://github.com/elapouya/python-docx-template/issues

---

**Made with ❤️ by AI Assistant**
**Date: 2025-11-26**
