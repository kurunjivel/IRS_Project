import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
});

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('irs_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    console.error('API Request Error:', error);
    if (error.response && error.response.status === 401) {
      // Clear invalid session if unauthenticated
      if (!window.location.pathname.includes('/login')) {
        localStorage.removeItem('irs_token');
        localStorage.removeItem('irs_user');
      }
    }
    return Promise.reject(error);
  }
);

export default api;
