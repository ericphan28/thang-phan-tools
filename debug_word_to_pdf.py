"""
Debug Word to PDF conversion issue
"""

import sys
from pathlib import Path

# Test 1: Check LibreOffice
print("="*60)
print("TEST 1: LibreOffice")
print("="*60)
try:
    import subprocess
    result = subprocess.run(["soffice", "--version"], capture_output=True, text=True, timeout=5)
    if result.returncode == 0:
        print("✅ LibreOffice found:")
        print(f"   {result.stdout.strip()}")
    else:
        print("❌ LibreOffice command failed")
        print(f"   stderr: {result.stderr}")
except FileNotFoundError:
    print("❌ LibreOffice not found in PATH")
    print("   Install: winget install TheDocumentFoundation.LibreOffice")
except Exception as e:
    print(f"❌ Error testing LibreOffice: {e}")

# Test 2: Check docx2pdf
print("\n" + "="*60)
print("TEST 2: docx2pdf")
print("="*60)
try:
    from docx2pdf import convert
    print("✅ docx2pdf is installed")
    print("   But requires Microsoft Word to be installed")
except ImportError:
    print("❌ docx2pdf not installed")
    print("   Install: pip install docx2pdf")

# Test 3: Check win32com / Microsoft Word
print("\n" + "="*60)
print("TEST 3: Microsoft Word COM")
print("="*60)
try:
    import win32com.client
    print("✅ win32com is installed")
    
    try:
        import pythoncom
        pythoncom.CoInitialize()
        word = win32com.client.Dispatch("Word.Application")
        version = word.Version
        word.Quit()
        pythoncom.CoUninitialize()
        print(f"✅ Microsoft Word is installed (Version: {version})")
    except Exception as e:
        print(f"❌ Microsoft Word not accessible: {e}")
        print("   Please install Microsoft Office")
        
except ImportError:
    print("❌ win32com not installed")
    print("   Install: pip install pywin32")

# Summary
print("\n" + "="*60)
print("SUMMARY")
print("="*60)
print("For Word to PDF conversion to work, you need AT LEAST ONE of:")
print("1. LibreOffice installed and in PATH")
print("2. Microsoft Word installed (for docx2pdf or COM)")
print("3. Both docx2pdf package + Microsoft Word")
print("\nRecommended: Install LibreOffice (free, open source)")
print("Command: winget install TheDocumentFoundation.LibreOffice")
print("\nAfter installation, you may need to restart your PC.")
