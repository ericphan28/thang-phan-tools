# Test PDF to Word Smart - Quick Test
# Tạo PDF đơn giản để test với font hỗ trợ tiếng Việt

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

def create_test_pdf():
    # Register Unicode font (Times New Roman có sẵn trên Windows)
    try:
        # Thử dùng Times New Roman từ Windows
        pdfmetrics.registerFont(TTFont('TimesVN', 'C:\\Windows\\Fonts\\times.ttf'))
        pdfmetrics.registerFont(TTFont('TimesVN-Bold', 'C:\\Windows\\Fonts\\timesbd.ttf'))
        font_name = 'TimesVN'
        font_bold = 'TimesVN-Bold'
    except:
        # Fallback: dùng DejaVu (nếu có)
        try:
            pdfmetrics.registerFont(TTFont('DejaVu', 'C:\\Windows\\Fonts\\DejaVuSans.ttf'))
            pdfmetrics.registerFont(TTFont('DejaVu-Bold', 'C:\\Windows\\Fonts\\DejaVuSans-Bold.ttf'))
            font_name = 'DejaVu'
            font_bold = 'DejaVu-Bold'
        except:
            # Fallback cuối: dùng Arial
            pdfmetrics.registerFont(TTFont('ArialVN', 'C:\\Windows\\Fonts\\arial.ttf'))
            pdfmetrics.registerFont(TTFont('ArialVN-Bold', 'C:\\Windows\\Fonts\\arialbd.ttf'))
            font_name = 'ArialVN'
            font_bold = 'ArialVN-Bold'
    
    c = canvas.Canvas("test_layout.pdf", pagesize=letter)
    width, height = letter
    
    # Title - center
    c.setFont(font_bold, 16)
    title = "HỘI NÔNG DÂN VIỆT NAM"
    title_width = c.stringWidth(title, font_bold, 16)
    c.drawString((width - title_width) / 2, height - 1*inch, title)
    
    # Subtitle - center
    c.setFont(font_name, 12)
    subtitle = "BCH HỘI NÔNG DÂN XÃ GIA KIỆM"
    subtitle_width = c.stringWidth(subtitle, font_name, 12)
    c.drawString((width - subtitle_width) / 2, height - 1.3*inch, subtitle)
    
    # Document number - left
    c.setFont(font_name, 11)
    c.drawString(1*inch, height - 2*inch, "Số 04-CV/HNDX")
    
    # Date - right
    date_text = "Gia Kiệm, ngày 17 tháng 12 năm 2025"
    date_width = c.stringWidth(date_text, font_name, 11)
    c.drawString(width - date_width - 1*inch, height - 2*inch, date_text)
    
    # Greeting - center
    c.setFont(font_bold, 12)
    greeting = "Kính gửi: Các chi hội và tổ hội"
    greeting_width = c.stringWidth(greeting, font_bold, 12)
    c.drawString((width - greeting_width) / 2, height - 2.8*inch, greeting)
    
    # Body text
    c.setFont(font_name, 11)
    body = [
        "     Thực hiện Hướng dẫn số 1093-CV/HNDT ngày 15/12/2025 của Ban Thường",
        "trực Ủy Ban Mặt trận Tổ quốc Việt Nam tỉnh về hướng dẫn tuyên truyền cuộc bầu",
        "cử đại biểu Quốc hội khoá XVI và đại biểu Hội đồng nhân dân các cấp nhiệm kỳ",
        "2026 - 2031; Ban Thường vụ Hội Nông dân xã đề nghị các chi hội và tổ hội các",
        "ấp, triển khai thực hiện một số nhiệm vụ sau:",
    ]
    
    y_position = height - 3.5*inch
    for line in body:
        c.drawString(1.2*inch, y_position, line)
        y_position -= 0.25*inch
    
    # Numbered list
    c.setFont(font_bold, 11)
    c.drawString(1.2*inch, y_position - 0.2*inch, "1. Tuyên truyền sâu rộng:")
    
    c.setFont(font_name, 11)
    list_text = [
        "- Nâng cao nhận thức của cán bộ, hội viên nông dân về ý nghĩa",
        "- Góp phần tạo sự thống nhất về tư tưởng"
    ]
    y_position -= 0.5*inch
    for item in list_text:
        c.drawString(1.5*inch, y_position, item)
        y_position -= 0.25*inch
    
    c.save()
    print("✅ Created test_layout.pdf with Vietnamese font support")

if __name__ == "__main__":
    create_test_pdf()
