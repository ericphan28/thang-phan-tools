#!/usr/bin/env python3
"""
Test script for Text to Word (MHTML) feature
"""
import requests
import json
from pathlib import Path

BASE_URL = "http://localhost:8000"

# Test data
TEST_TEXT = """Báo cáo tiến độ dự án Website Thương mại điện tử

Thông tin dự án: Dự án phát triển website thương mại điện tử cho công ty ABC được khởi động từ tháng 1/2025 với mục tiêu tạo ra một nền tảng mua sắm trực tuyến hiện đại, thân thiện với người dùng.

Các tính năng chính đã phát triển:
- Hệ thống tìm kiếm và lọc sản phẩm thông minh với AI
- Giỏ hàng và thanh toán đa phương thức (VNPay, MoMo, COD)
- Quản lý đơn hàng realtime với WebSocket
- Hệ thống đánh giá và phản hồi tích hợp rating 5 sao

Tiến độ thực hiện chi tiết:

Giai đoạn 1 (Tháng 1-2): Phân tích yêu cầu và thiết kế UI/UX đã hoàn thành 100%. Team design đã tạo được mockup cho 25 màn hình chính và prototype tương tác trên Figma.

Giai đoạn 2 (Tháng 3-4): Phát triển backend API đạt 85% với FastAPI và PostgreSQL. Frontend React đạt 70% với Material-UI và Redux Toolkit.

Thành viên team tham gia:

Backend team: Nguyễn Văn An (Tech Lead), Trần Thị Bình (Senior Developer), Lê Văn Cường (Junior Developer).

Frontend team: Phạm Thị Dung (Frontend Lead), Hoàng Văn Em (React Developer), Đỗ Thị Phương (UI/UX Designer).

Kết luận: Dự án đang đi đúng tiến độ và chất lượng đảm bảo. Team làm việc hiệu quả với daily standup và sprint planning 2 tuần/lần. Dự kiến hoàn thành và đưa vào sử dụng vào cuối tháng 4/2025 với full features như kế hoạch ban đầu.
"""


def test_text_to_word_gemini():
    """Test with Gemini provider"""
    print("\n" + "="*80)
    print("🧪 TEST 1: Text to Word with GEMINI")
    print("="*80)
    
    data = {
        "text": TEST_TEXT,
        "provider": "gemini",
        "language": "vi"
    }
    
    try:
        print("📤 Sending request to API...")
        response = requests.post(
            f"{BASE_URL}/api/v1/documents/text-to-word-smart",
            data=data,
            timeout=120
        )
        
        if response.status_code == 200:
            # Save file
            output_path = Path("output_gemini.doc")
            with open(output_path, 'wb') as f:
                f.write(response.content)
            
            # Print metadata
            print("\n✅ SUCCESS!")
            print(f"📄 File saved: {output_path.absolute()}")
            print(f"📊 File size: {len(response.content) / 1024:.2f} KB")
            
            # Print headers
            print("\n📋 Response Headers:")
            for key in ['x-technology-engine', 'x-technology-name', 'x-technology-model', 
                       'x-input-tokens', 'x-output-tokens', 'x-processing-time-ms']:
                if key in response.headers:
                    print(f"  • {key}: {response.headers[key]}")
        else:
            print(f"\n❌ ERROR: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"\n❌ EXCEPTION: {e}")


def test_text_to_word_claude():
    """Test with Claude provider"""
    print("\n" + "="*80)
    print("🧪 TEST 2: Text to Word with CLAUDE")
    print("="*80)
    
    data = {
        "text": TEST_TEXT,
        "provider": "claude",
        "model": "claude-3-5-sonnet-20241022",
        "language": "vi"
    }
    
    try:
        print("📤 Sending request to API...")
        response = requests.post(
            f"{BASE_URL}/api/v1/documents/text-to-word-smart",
            data=data,
            timeout=120
        )
        
        if response.status_code == 200:
            # Save file
            output_path = Path("output_claude.doc")
            with open(output_path, 'wb') as f:
                f.write(response.content)
            
            # Print metadata
            print("\n✅ SUCCESS!")
            print(f"📄 File saved: {output_path.absolute()}")
            print(f"📊 File size: {len(response.content) / 1024:.2f} KB")
            
            # Print headers
            print("\n📋 Response Headers:")
            for key in ['x-technology-engine', 'x-technology-name', 'x-technology-model', 
                       'x-input-tokens', 'x-output-tokens', 'x-processing-time-ms']:
                if key in response.headers:
                    print(f"  • {key}: {response.headers[key]}")
        else:
            print(f"\n❌ ERROR: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"\n❌ EXCEPTION: {e}")


def test_get_providers():
    """Test get available providers"""
    print("\n" + "="*80)
    print("🧪 TEST 3: Get Available AI Providers")
    print("="*80)
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/documents/ai-providers")
        
        if response.status_code == 200:
            data = response.json()
            print("\n✅ SUCCESS!")
            print(f"\n📋 Available Providers: {len(data['providers'])}")
            
            for provider in data['providers']:
                print(f"\n  🤖 {provider['name']} ({provider['id']})")
                print(f"     Status: {provider['status']}")
                print(f"     Recommended: {provider['recommended']}")
                print(f"     Models: {len(provider['models'])}")
                for model in provider['models'][:2]:  # Show first 2 models
                    print(f"       • {model['name']} (Q:{model['quality']}/10, S:{model['speed']}/10)")
        else:
            print(f"\n❌ ERROR: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"\n❌ EXCEPTION: {e}")


if __name__ == "__main__":
    print("\n🚀 TEXT TO WORD (MHTML) - COMPREHENSIVE TEST")
    print("="*80)
    
    # Test 1: Gemini
    test_text_to_word_gemini()
    
    # Test 2: Claude (comment out if no Claude API key)
    # test_text_to_word_claude()
    
    # Test 3: Get providers
    test_get_providers()
    
    print("\n" + "="*80)
    print("✅ ALL TESTS COMPLETED!")
    print("="*80)
    print("\n💡 TIP: Open the .doc files with Microsoft Word to see the formatting!")
    print("   Files: output_gemini.doc, output_claude.doc")
    print()
