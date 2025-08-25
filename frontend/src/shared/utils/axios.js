import axios from 'axios';
import Cookies from 'js-cookie';
import use_auth_store from '../stores/use_auth_store';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Create axios instance
const axios_instance = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true, // Important: send cookies with requests
  headers: {
    'Content-Type': 'application/json',
    'X-Client-Type': 'web'  // Explicitly identify as web client
  },
});

// Request interceptor - add CSRF token to requests
axios_instance.interceptors.request.use(
  (config) => {
    // Add CSRF token for state-changing requests (web clients only)
    if (['post', 'put', 'patch', 'delete'].includes(config.method.toLowerCase())) {
      const csrf_token = Cookies.get('csrf_token');
      if (csrf_token) {
        config.headers['X-CSRF-Token'] = csrf_token;
      }
    }
    
    // The Authorization header will be set by the auth store for mobile/API clients
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor - handle token refresh
axios_instance.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original_request = error.config;
    
    // If 401 and not already retried, try to refresh token
    if (error.response?.status === 401 && !original_request._retry) {
      original_request._retry = true;
      
      // Get auth store to check client type
      const auth_store = use_auth_store.getState();
      
      if (auth_store.client_type === 'web') {
        // Web client - server handles refresh via cookies
        try {
          await axios_instance.post('/auth/refresh');
          // Retry original request
          return axios_instance(original_request);
        } catch (refresh_error) {
          // Refresh failed, redirect to login
          window.location.href = '/auth/login';
          return Promise.reject(refresh_error);
        }
      } else {
        // Mobile/API client - use refresh token from store
        const refresh_success = await auth_store.refresh_access_token();
        if (refresh_success) {
          // Retry with new token
          return axios_instance(original_request);
        } else {
          // Refresh failed, need to login again
          return Promise.reject(error);
        }
      }
    }
    
    return Promise.reject(error);
  }
);

export default axios_instance;