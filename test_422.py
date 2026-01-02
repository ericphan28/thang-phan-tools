#!/usr/bin/env python3
"""Test wrong FormData field"""
import requests

url = "http://localhost:8000/api/v1/documents/ocr-to-word"
pdf_file = "test_pdf_with_text.pdf"

print("Testing with WRONG field name:")
with open(pdf_file, 'rb') as f:
    files = {'wrongfield': (pdf_file, f, 'application/pdf')}
    response = requests.post(url, files=files)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
print("\n" + "="*50)
print("Testing with CORRECT field name:")
with open(pdf_file, 'rb') as f:
    files = {'file': (pdf_file, f, 'application/pdf')}
    response = requests.post(url, files=files)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"SUCCESS! {len(response.content)} bytes")
    else:
        print(f"Response: {response.text}")
