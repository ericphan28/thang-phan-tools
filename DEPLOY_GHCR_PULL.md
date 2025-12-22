# Deploy nhanh nhất: GitHub Actions build image + VPS chỉ pull

Mục tiêu: không build Docker trên VPS (rất lâu với OpenCV/Tesseract/matplotlib…), thay vào đó build trên GitHub Actions có cache, rồi VPS chỉ pull image và restart.

## 1) GitHub Actions sẽ publish image nào?
Workflow: `.github/workflows/backend-image-ghcr.yml`

Images (GHCR):
- Backend: `ghcr.io/ericphan28/thang-phan-tools-backend:latest`
- Frontend: `ghcr.io/ericphan28/thang-phan-tools-frontend:latest`

Tag thêm theo commit:
- `sha-<short>`

## 2) Chuẩn bị GHCR quyền pull
Có 2 lựa chọn:

### A) Public packages (dễ nhất)
- Set package visibility là **Public** trong GHCR
- VPS pull không cần login

### B) Private packages (an toàn hơn)
- Tạo GitHub Personal Access Token (PAT) có quyền `read:packages`
- Trên VPS:
  - `docker login ghcr.io -u <github_username> -p <PAT>`

## 3) Cấu hình VPS để dùng compose pull
Trên VPS, trong thư mục deploy (vd: `/opt/utility-server`) tạo file `.env` (hoặc export env vars) có tối thiểu:

- `BACKEND_IMAGE=ghcr.io/<OWNER>/<REPO>-backend:latest`
- `FRONTEND_IMAGE=ghcr.io/<OWNER>/<REPO>-frontend:latest`

Ví dụ đúng cho repo hiện tại:
- `BACKEND_IMAGE=ghcr.io/ericphan28/thang-phan-tools-backend:latest`
- `FRONTEND_IMAGE=ghcr.io/ericphan28/thang-phan-tools-frontend:latest`

Và các biến môi trường sẵn có của app:
- `DB_PASSWORD=...`
- `REDIS_PASSWORD=...`
- `SECRET_KEY=...`
- `JWT_SECRET_KEY=...`

Sau đó deploy:
- `docker compose -f docker-compose.prod.yml pull`
- `docker compose -f docker-compose.prod.yml up -d`

## 4) Update nhanh mỗi lần release
Chỉ cần:
- `git pull`
- `docker compose -f docker-compose.prod.yml pull`
- `docker compose -f docker-compose.prod.yml up -d`

## Notes
- Backend Docker image cài từ `backend/requirements-prod.txt` (không cài test/dev tools).
- Frontend image build bằng `frontend/Dockerfile.prod` và mặc định `VITE_API_BASE_URL=/api/v1`.
