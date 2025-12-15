"""
Convert .doc to .docx using win32com (Word automation)
Chỉ chạy được trên Windows với Microsoft Word đã cài đặt
"""
import os
import sys

try:
    import win32com.client
except ImportError:
    print("❌ Cần cài đặt: pip install pywin32")
    sys.exit(1)

# Paths
doc_file = r"d:\thang\utility-server\templates\mau-nha-nuoc\so-yeu-ly-lich.doc"
docx_file = r"d:\thang\utility-server\templates\so_yeu_ly_lich_goc.docx"

print(f"🔄 Converting: {doc_file}")
print(f"📝 To: {docx_file}")

# Start Word
word = win32com.client.Dispatch("Word.Application")
word.Visible = False

try:
    # Open .doc file
    doc = word.Documents.Open(doc_file)
    
    # Save as .docx (format 16 = docx)
    doc.SaveAs2(docx_file, FileFormat=16)
    
    # Close
    doc.Close()
    
    print(f"✅ Converted successfully!")
    print(f"📄 File: {docx_file}")
    print(f"📏 Size: {os.path.getsize(docx_file)} bytes")
    
except Exception as e:
    print(f"❌ Error: {e}")
finally:
    word.Quit()
