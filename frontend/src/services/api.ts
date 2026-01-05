import axios from 'axios';
import { config } from '../config';

const api = axios.create({
  baseURL: config.apiUrl,
  headers: {
    'Content-Type': 'application/json',
  },
  // TIMEOUT OPTIMIZATION: Match backend settings
  timeout: 300000, // 5 minutes for file processing (matches backend)
  maxContentLength: 200 * 1024 * 1024, // 200MB max request size
  maxBodyLength: 200 * 1024 * 1024, // 200MB max body size
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
    
    // DYNAMIC TIMEOUT: Estimate based on file size
    const files = Array.from(config.data.entries()).filter(([key, value]) => 
      value instanceof File
    );
    
    if (files.length > 0) {
      const totalSize = files.reduce((sum, [key, file]) => 
        sum + (file as File).size, 0
      );
      const sizeInMB = totalSize / (1024 * 1024);
      
      // Dynamic timeout: 30s base + 10s per MB, max 5 minutes
      const dynamicTimeout = Math.min(30000 + (sizeInMB * 10000), 300000);
      config.timeout = dynamicTimeout;
      
      console.log(`📊 File size: ${sizeInMB.toFixed(1)}MB, Timeout: ${dynamicTimeout/1000}s`);
    }
  }
  
  return config;
});

// Handle 401 errors and timeout errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Handle authentication errors
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      window.location.href = '/login';
      return Promise.reject(error);
    }
    
    // Handle timeout errors with user-friendly messages
    if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
      console.error('⏰ Request timeout:', error.message);
      return Promise.reject({
        ...error,
        message: 'Xử lý quá lâu. Vui lòng thử lại với file nhỏ hơn hoặc kiểm tra kết nối mạng.',
        isTimeout: true
      });
    }
    
    // Handle 408 Request Timeout from server
    if (error.response?.status === 408) {
      console.error('⏰ Server timeout (408):', error.response.data);
      return Promise.reject({
        ...error,
        message: 'Server xử lý quá lâu. File có thể quá lớn. Vui lòng thử lại với file nhỏ hơn.',
        isTimeout: true
      });
    }
    
    return Promise.reject(error);
  }
);

export default api;
