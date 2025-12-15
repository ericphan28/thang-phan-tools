#!/usr/bin/env python3
"""Simple test for Split PDF API"""
import requests
from pathlib import Path

BASE_URL = "http://localhost:8000/api/v1"

# Login
print("Logging in...")
response = requests.post(f"{BASE_URL}/auth/login", json={"username": "admin", "password": "admin123"})
if response.status_code != 200:
    print(f"Login failed: {response.status_code}")
    exit(1)

token = response.json()['token']['access_token']
print(f"Token received: {token[:30]}...")

# Find PDF
pdf_path = Path("backend/uploads/outputs/1.3. Nội quy, quy chế Đại hội.pdf")
if not pdf_path.exists():
    pdfs = list(Path("backend/uploads/outputs").glob("*.pdf"))
    if pdfs:
        pdf_path = pdfs[0]
    else:
        print("No PDF found!")
        exit(1)

print(f"\nTesting Split PDF with: {pdf_path.name}")
print(f"Size: {pdf_path.stat().st_size / 1024:.1f} KB")

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

print(f"\nStatus Code: {response.status_code}")

if response.status_code == 200:
    print("SUCCESS! Split PDF works!")
    # Save output
    with open("split_output.pdf", 'wb') as out:
        out.write(response.content)
    print(f"Output saved to: split_output.pdf ({len(response.content)} bytes)")
else:
    print(f"FAILED!")
    print(f"Error: {response.text}")
