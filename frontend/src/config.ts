// Use relative URL to work with Nginx proxy
// In production: http://165.99.59.47/api -> Nginx proxies to backend:8000
// In development: can override with VITE_API_URL env variable
export const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

export const config = {
  apiUrl: API_BASE_URL,
};
