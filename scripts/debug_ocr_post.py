import requests
from pathlib import Path

URL = "http://localhost:8000/api/v1/documents/ocr-to-word"
PDFS = [
    Path(r"D:\Thang\thang-phan-tools\test_layout.pdf"),
    Path(r"D:\Thang\thang-phan-tools\test_pdf_with_text.pdf"),
    Path(r"D:\Thang\thang-phan-tools\split_output.pdf"),
]

for pdf in PDFS:
    print(f"\n==> {pdf.name}")
    with pdf.open("rb") as f:
        files = {"file": (pdf.name, f, "application/pdf")}
        resp = requests.post(URL, files=files, timeout=120)

    print("status:", resp.status_code)
    print("content-type:", resp.headers.get("content-type"))
    print("content-length:", resp.headers.get("content-length"))

    if resp.status_code == 200:
        out = Path(r"D:\Thang\thang-phan-tools") / f"debug_{pdf.stem}.docx"
        out.write_bytes(resp.content)
        print("saved:", out)
    else:
        print(resp.text)
