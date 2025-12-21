# Utility Server

FastAPI backend (8000) + React/TS frontend (5173). JWT auth.

## Structure
- `backend/app/api/v1/endpoints/` - REST APIs
- `backend/app/routers/` - adobe_pdf_services, mau_2c
- `backend/app/services/` - business logic
- `frontend/src/pages/` - React pages
- `frontend/src/services/api.ts` - Axios client

## Run Servers
**ALWAYS use VS Code tasks - NEVER manual commands:**
- `Ctrl+Shift+P` → "Run Task" → "Start All Servers"
- Or use terminal UI: select "Backend Server" + "Frontend Server" tasks

## Patterns
- Pydantic schemas for validation
- File uploads → temp_uploads → process → cleanup
- Frontend uses Radix UI + Tailwind + react-hot-toast
- AI Admin: `/api/v1/ai-admin/*` endpoints for Gemini/Claude usage tracking
