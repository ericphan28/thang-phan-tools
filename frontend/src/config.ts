// Production: Use relative URL - Nginx proxies /api/v1/* to backend:8000/api/v1/*
// Development: Use localhost:8000/api/v1
const isProd = import.meta.env.PROD;
export const API_BASE_URL = isProd ? '/api/v1' : (import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1');

export const config = {
  apiUrl: API_BASE_URL,
};
