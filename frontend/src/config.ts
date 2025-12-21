// Use relative URL to work with Nginx proxy
// In production: http://165.99.59.47/api/v1 -> Nginx proxies to backend:8000/api/v1
// In development: Override with VITE_API_URL env variable or use localhost:8000
// Updated: 2025-12-18 - Fixed for local development
export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export const config = {
  apiUrl: API_BASE_URL,
};
