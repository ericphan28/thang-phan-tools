#!/usr/bin/env python3
"""Test Split PDF with protected file"""
import requests
from pathlib import Path

BASE_URL = "http://localhost:8000/api/v1"

# Login
print("Logging in...")
response = requests.post(f"{BASE_URL}/auth/login", json={"username": "admin", "password": "admin123"})
token = response.json()['token']['access_token']
print(f"Token: OK\n")

# Test with PROTECTED PDF
pdf_path = Path("backend/uploads/outputs/báo giá cá  03   151125_protected.pdf")
if not pdf_path.exists():
    print(f"Protected PDF not found: {pdf_path}")
    exit(1)

print(f"Testing Split PDF with PROTECTED file:")
print(f"File: {pdf_path.name}")
print(f"Size: {pdf_path.stat().st_size / 1024:.1f} KB\n")

# Test Split PDF
headers = {"Authorization": f"Bearer {token}"}
with open(pdf_path, 'rb') as f:
    files = {'file': (pdf_path.name, f, 'application/pdf')}
    data = {'page_ranges': '1-2', 'output_prefix': 'test'}
    
    response = requests.post(
        f"{BASE_URL}/documents/pdf/split",
        headers=headers,
        files=files,
        data=data
    )

print(f"Status Code: {response.status_code}")

if response.status_code == 200:
    print("UNEXPECTED SUCCESS! Should have failed with protected PDF")
else:
    print(f"Expected failure!")
    print(f"Error message: {response.json()['detail']}")
    print("\nThis is correct behavior - protected PDFs should be rejected with clear message.")
