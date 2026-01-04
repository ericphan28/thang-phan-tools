#!/usr/bin/env python3
"""
Test script để phát hiện và test HTML entity conversion

Usage:
python test_html_entity_detection.py
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from app.services.ocr_service import OCRService
from app.services.gemini_service import GeminiService
from app.core.database import get_db
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)

def test_html_entity_conversion():
    """
    Test HTML entity conversion với các trường hợp phổ biến
    Giúp phát hiện những entity nào chưa được handle
    """
    
    # Create mock services for testing
    db_gen = get_db()
    db = next(db_gen)
    gemini_service = GeminiService(db, user_id=1)  # Mock user ID
    ocr_service = OCRService(gemini_service)
    
    # Test cases: các HTML entities có thể xuất hiện trong Gemini output
    test_cases = [
        # Basic HTML tags
        ("Text with <br/> line break", "Text with \n line break"),
        ("Text with <br> line break", "Text with \n line break"),
        ("Text with <p>paragraph</p>", "Text with paragraph"),
        
        # Common HTML entities
        ("Hello&nbsp;world", "Hello world"),
        ("AT&amp;T company", "AT&T company"),
        ("Price &lt;$100&gt;", "Price <$100>"),
        ("Quote: &quot;Hello&quot;", 'Quote: "Hello"'),
        ("Don&#39;t worry", "Don't worry"),
        
        # Vietnamese HTML entities (common in government docs)
        ("T&aacute;i liệu", "Tái liệu"),
        ("Th&ocirc;ng tin", "Thông tin"),
        ("B&aacute;o c&aacute;o", "Báo cáo"),
        ("Quy&ecirc;t định", "Quyết định"),
        
        # Numeric entities (Unicode)
        ("Gi&aacute; tr&#7883;", "Giá trị"),  # &#7883; = ị
        ("Th&#7889;i gian", "Thời gian"),   # &#7889; = ời
        
        # Complex cases
        ("Line 1<br/>Line 2&nbsp;&nbsp;with spaces", "Line 1\nLine 2  with spaces"),
        ("HTML: &lt;div class=&quot;test&quot;&gt;Content&lt;/div&gt;", 'HTML: <div class="test">Content</div>'),
        
        # Edge cases that might not be handled
        ("Unknown: &unknown123; entity", "Unknown: &unknown123; entity"),  # Should detect this
        ("Custom tag: <customtag>content</customtag>", "Custom tag: content"),
        
        # Vietnamese government document samples
        ("C&ocirc;ng văn số 123/2024/QĐ-TTg", "Công văn số 123/2024/QĐ-TTg"),
        ("Ng&agrave;y 31 th&aacute;ng 12 năm 2024", "Ngày 31 tháng 12 năm 2024"),
    ]
    
    print("🧪 TESTING HTML ENTITY CONVERSION")
    print("=" * 50)
    
    passed = 0
    failed = 0
    detected_issues = []
    
    for i, (input_text, expected) in enumerate(test_cases, 1):
        result = ocr_service._convert_html_tags_to_text(input_text)
        
        print(f"\nTest {i}:")
        print(f"Input:    '{input_text}'")
        print(f"Expected: '{expected}'")
        print(f"Result:   '{result}'")
        
        if result == expected:
            print("✅ PASS")
            passed += 1
        else:
            print("❌ FAIL")
            failed += 1
            detected_issues.append({
                'input': input_text,
                'expected': expected,
                'actual': result
            })
    
    print("\n" + "=" * 50)
    print(f"📊 TEST SUMMARY: {passed} passed, {failed} failed")
    
    if detected_issues:
        print("\n🔍 ISSUES DETECTED:")
        for issue in detected_issues[:3]:  # Show first 3 issues
            print(f"- Input: '{issue['input']}'")
            print(f"  Expected: '{issue['expected']}'")
            print(f"  Got:      '{issue['actual']}'")
    
    # Cleanup database connection
    db.close()
    
    return passed, failed

def test_detection_system():
    """
    Test the detection system with problematic content
    """
    print("\n🔍 TESTING DETECTION SYSTEM")
    print("=" * 50)
    
    db_gen = get_db()
    db = next(db_gen)
    gemini_service = GeminiService(db, user_id=1)  # Mock user ID
    ocr_service = OCRService(gemini_service)
    
    # Content with various unhandled entities to test detection
    problematic_content = """
    Document contains:
    - Unknown entity: &unknownEntity;
    - Numeric entity: &#9999;
    - Custom tag: <customtag>content</customtag>
    - Malformed: &incomplete
    - Vietnamese: cần thiết cho việc thực hiện
    - Mixed: Text with <span class="highlight">highlighted</span> content
    """
    
    print("Processing problematic content to test detection...")
    result = ocr_service._convert_html_tags_to_text(problematic_content)
    print(f"Result length: {len(result)} characters")
    
    # Cleanup database connection
    db.close()
    
    return result

if __name__ == "__main__":
    print("🚀 HTML Entity Detection Test Suite")
    print("Giúp phát hiện HTML entities/tags chưa được handle trong OCR output")
    
    try:
        # Test conversion accuracy
        passed, failed = test_html_entity_conversion()
        
        # Test detection system 
        test_result = test_detection_system()
        
        print(f"\n✨ Testing completed!")
        print(f"Check logs above for any detected unhandled HTML entities")
        print(f"If you see warnings ⚠️, consider adding those entities to the conversion logic")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()