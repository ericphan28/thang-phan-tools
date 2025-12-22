# Deploy nhanh (VPS)

Mục tiêu: giảm thời gian `docker-compose up -d --build backend` bằng cách:
- Cắt bỏ dev/test dependencies khỏi production image
- Bật pip cache BuildKit đúng cách
- Tránh bind-mount source code vào container production

## Thay đổi chính
- Backend production image cài từ `backend/requirements-prod.txt`
- Local dev vẫn dùng `backend/requirements.txt` (bao gồm cả prod + dev)
- `docker-compose.yml` (production) không còn mount `./backend:/app`

## Deploy trên VPS
- Bật BuildKit để build cache hiệu quả:
  - `export DOCKER_BUILDKIT=1`
  - `export COMPOSE_DOCKER_CLI_BUILD=1`
- Rebuild backend:
  - `docker-compose up -d --build backend`

## Local development
- Nếu bạn cài python deps local:
  - `pip install -r backend/requirements.txt`

## Gợi ý tối ưu cao hơn (nhanh nhất)
- Build image trên GitHub Actions và push lên registry (GHCR/Docker Hub)
- VPS chỉ `docker-compose pull && docker-compose up -d` (thường nhanh hơn rất nhiều)
