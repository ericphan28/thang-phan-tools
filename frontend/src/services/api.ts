import axios from 'axios';
import { config } from '../config';

const api = axios.create({
  baseURL: config.apiUrl,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
api.interceptors.request.use((config) => {
  const skipAuth = (config.headers as any)?.['X-Skip-Auth'] === 'true';

  const token = localStorage.getItem('access_token');
  if (token && !skipAuth && !config.headers.Authorization) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  // Don't send this internal header to backend
  if ((config.headers as any)?.['X-Skip-Auth']) {
    delete (config.headers as any)['X-Skip-Auth'];
  }
  
  // If sending FormData, remove Content-Type to let browser set it with boundary
  if (config.data instanceof FormData) {
    delete config.headers['Content-Type'];
  }
  
  return config;
});

// Handle 401 errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;
