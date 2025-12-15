"""Test Technology Metadata API"""
import requests
from pathlib import Path

API_BASE = "http://localhost:8000/api"

def test_word_to_pdf():
    """Test Word to PDF conversion with technology metadata"""
    print("\n=== Testing Word → PDF (Gotenberg) ===")
    
    # Find a test Word file
    test_files = list(Path(".").glob("*.docx"))
    if not test_files:
        print("❌ No .docx file found in current directory")
        return
    
    test_file = test_files[0]
    print(f"📄 Using file: {test_file}")
    
    with open(test_file, 'rb') as f:
        files = {'file': (test_file.name, f, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')}
        
        response = requests.post(
            f"{API_BASE}/documents/convert/word-to-pdf",
            files=files
        )
    
    if response.status_code == 200:
        print("✅ Conversion successful!")
        print(f"📊 Content-Type: {response.headers.get('content-type')}")
        
        # Check technology headers
        tech_engine = response.headers.get('X-Technology-Engine')
        tech_name = response.headers.get('X-Technology-Name')
        tech_quality = response.headers.get('X-Technology-Quality')
        
        if tech_engine:
            print(f"🔥 Technology Engine: {tech_engine}")
            print(f"📝 Technology Name: {tech_name}")
            print(f"⭐ Quality: {tech_quality}")
        else:
            print("⚠️ No technology headers found in response")
            
        print(f"📦 Response size: {len(response.content)} bytes")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)

def test_pdf_to_word():
    """Test PDF to Word conversion with technology metadata"""
    print("\n=== Testing PDF → Word (Adobe/pdf2docx) ===")
    
    # Find a test PDF file
    test_files = list(Path(".").glob("*.pdf"))
    if not test_files:
        print("❌ No .pdf file found in current directory")
        return
    
    test_file = test_files[0]
    print(f"📄 Using file: {test_file}")
    
    with open(test_file, 'rb') as f:
        files = {'file': (test_file.name, f, 'application/pdf')}
        
        response = requests.post(
            f"{API_BASE}/documents/convert/pdf-to-word",
            files=files
        )
    
    if response.status_code == 200:
        print("✅ Conversion successful!")
        print(f"📊 Content-Type: {response.headers.get('content-type')}")
        
        # Check technology headers
        tech_engine = response.headers.get('X-Technology-Engine')
        tech_name = response.headers.get('X-Technology-Name')
        tech_quality = response.headers.get('X-Technology-Quality')
        tech_quota = response.headers.get('X-Adobe-Quota-Remaining')
        
        if tech_engine:
            print(f"🔥 Technology Engine: {tech_engine}")
            print(f"📝 Technology Name: {tech_name}")
            print(f"⭐ Quality: {tech_quality}")
            if tech_quota:
                print(f"📊 Adobe Quota: {tech_quota}")
        else:
            print("⚠️ No technology headers found in response")
            
        print(f"📦 Response size: {len(response.content)} bytes")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)

def test_pdf_to_excel():
    """Test PDF to Excel conversion with technology metadata"""
    print("\n=== Testing PDF → Excel (pdfplumber) ===")
    
    # Find a test PDF file
    test_files = list(Path(".").glob("*.pdf"))
    if not test_files:
        print("❌ No .pdf file found in current directory")
        return
    
    test_file = test_files[0]
    print(f"📄 Using file: {test_file}")
    
    with open(test_file, 'rb') as f:
        files = {'file': (test_file.name, f, 'application/pdf')}
        
        response = requests.post(
            f"{API_BASE}/documents/convert/pdf-to-excel",
            files=files
        )
    
    if response.status_code == 200:
        print("✅ Conversion successful!")
        print(f"📊 Content-Type: {response.headers.get('content-type')}")
        
        # Check technology headers
        tech_engine = response.headers.get('X-Technology-Engine')
        tech_name = response.headers.get('X-Technology-Name')
        tech_quality = response.headers.get('X-Technology-Quality')
        
        if tech_engine:
            print(f"🔥 Technology Engine: {tech_engine}")
            print(f"📝 Technology Name: {tech_name}")
            print(f"⭐ Quality: {tech_quality}")
        else:
            print("⚠️ No technology headers found in response")
            
        print(f"📦 Response size: {len(response.content)} bytes")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    print("🚀 Testing Technology Metadata API")
    print("=" * 60)
    
    # Test API health
    try:
        response = requests.get(f"{API_BASE.replace('/api', '')}/")
        if response.status_code == 200:
            print("✅ Backend is running")
            print(f"📡 Response: {response.json()}")
        else:
            print("❌ Backend not responding")
            exit(1)
    except Exception as e:
        print(f"❌ Cannot connect to backend: {e}")
        exit(1)
    
    # Run tests
    test_word_to_pdf()
    test_pdf_to_word()
    test_pdf_to_excel()
    
    print("\n" + "=" * 60)
    print("✅ Testing complete!")
