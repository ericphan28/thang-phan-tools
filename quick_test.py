import requests
import json

url = "http://127.0.0.1:8000/api/v1/ocr-compare/compare-engines"
files = {"file": open("d:/Thang/thang-phan-tools/test_files/ocr_vietnamese.png", "rb")}
data = {"engines": "adobe,tesseract,gemini", "language": "vie"}

print("Sending request...")
response = requests.post(url, files=files, data=data, timeout=60)
print(f"Status: {response.status_code}")

if response.status_code == 200:
    result = response.json()
    print(f"\n✅ SUCCESS!")
    print(f"File: {result['filename']}")
    print(f"Engines available: {len([e for e, d in result['engines'].items() if d.get('available')])}/3")
    print(f"\nEngines:")
    for engine, data in result['engines'].items():
        status = "✅" if data.get('available') else "❌"
        print(f"\n{status} {engine.upper()}:")
        if data.get('available'):
            print(f"   Text: {data.get('text', '')[:50]}...")
            print(f"   Time: {data.get('processing_time')}s")
        else:
            print(f"   Reason: {data.get('reason', data.get('error', 'Unknown'))}")
            if data.get('note'):
                print(f"   Note: {data.get('note')}")
else:
    print(f"Response: {response.text}")
