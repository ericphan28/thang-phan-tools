// Use relative URL to work with Nginx proxy
// In production: http://165.99.59.47/api/v1 -> Nginx proxies to backend:8000/api/v1
// In development: can override with VITE_API_URL env variable
// Updated: 2025-11-24 - Changed from /api to /api/v1
export const API_BASE_URL = import.meta.env.VITE_API_URL || '/api/v1';

export const config = {
  apiUrl: API_BASE_URL,
};
