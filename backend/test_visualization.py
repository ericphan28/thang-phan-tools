# -*- coding: utf-8 -*-
"""
Test Visualization Feature
Demo AI-powered document generation with charts
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.document_service import DocumentService


async def test_with_data():
    """Test text to Word with numerical data (should generate charts)"""
    
    text_with_data = """
    Báo Cáo Kinh Doanh Quý 4/2024
    
    Công ty đã đạt được những thành tựu đáng kể trong quý 4. Doanh thu các tháng như sau:
    - Tháng 10: 500 triệu đồng
    - Tháng 11: 650 triệu đồng  
    - Tháng 12: 720 triệu đồng
    
    So với quý 3, doanh thu quý 4 tăng trưởng 25%. Đây là mức tăng trưởng cao nhất trong năm.
    
    Phân tích chi tiết:
    - Sản phẩm A chiếm 45% doanh thu
    - Sản phẩm B chiếm 30% doanh thu
    - Sản phẩm C chiếm 25% doanh thu
    
    Kết luận: Xu hướng tăng trưởng ổn định, cần đầu tư thêm vào Sản phẩm A.
    """
    
    service = DocumentService()
    
    print("🚀 Testing with Gemini + Data Visualization...")
    print(f"Input text length: {len(text_with_data)} chars\n")
    
    try:
        docx_bytes, metadata = await service.text_to_word_mhtml(
            text=text_with_data,
            provider="gemini",
            model="gemini-2.0-flash-exp",
            language="vi"
        )
        
        # Save to file
        output_path = Path(__file__).parent / "test_output_with_charts.docx"
        with open(output_path, "wb") as f:
            f.write(docx_bytes)
        
        print(f"✅ Document created: {output_path}")
        print(f"📊 Processing time: {metadata.get('processing_time_ms', 0):.2f}ms")
        print(f"💰 Cost: ${metadata.get('total_cost_usd', 0):.4f}")
        
        # Check if AI created visualizations
        if "visualizations" in str(metadata):
            print("🎨 Visualizations detected!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


async def test_without_data():
    """Test text without data (no charts expected)"""
    
    text_no_data = """
    Giới Thiệu Về Python
    
    Python là một ngôn ngữ lập trình bậc cao, dễ học và mạnh mẽ. 
    Python được tạo ra bởi Guido van Rossum và phát hành lần đầu vào năm 1991.
    
    Ưu điểm của Python:
    - Cú pháp đơn giản, dễ đọc
    - Thư viện phong phú
    - Cộng đồng lớn mạnh
    - Đa năng (web, AI, data science...)
    
    Python hiện là một trong những ngôn ngữ lập trình phổ biến nhất thế giới.
    """
    
    service = DocumentService()
    
    print("\n🚀 Testing without Data (No charts expected)...")
    
    try:
        docx_bytes, metadata = await service.text_to_word_mhtml(
            text=text_no_data,
            provider="gemini",
            model="gemini-2.0-flash-exp",
            language="vi"
        )
        
        output_path = Path(__file__).parent / "test_output_no_charts.docx"
        with open(output_path, "wb") as f:
            f.write(docx_bytes)
        
        print(f"✅ Document created: {output_path}")
        print(f"📊 Processing time: {metadata.get('processing_time_ms', 0):.2f}ms")
        
    except Exception as e:
        print(f"❌ Error: {e}")


async def main():
    print("=" * 60)
    print("DATA VISUALIZATION TEST")
    print("=" * 60)
    
    # Test 1: With numerical data → Should generate charts
    await test_with_data()
    
    # Test 2: Without data → No charts
    await test_without_data()
    
    print("\n" + "=" * 60)
    print("✨ Tests completed! Check the output files.")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
