import axios from 'axios';

// API configuration
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const API_TIMEOUT = 30000; // 30 seconds

// Create axios instance
const apiClient = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  timeout: API_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Token management
const getAuthToken = () => {
  return localStorage.getItem('auth_token');
};

const setAuthToken = (token) => {
  if (token) {
    localStorage.setItem('auth_token', token);
  } else {
    localStorage.removeItem('auth_token');
  }
};

const clearAuthToken = () => {
  localStorage.removeItem('auth_token');
};

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    // Add auth token to requests
    const token = getAuthToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    // Add request timestamp for debugging
    config.metadata = { startTime: new Date() };

    // Log request in development
    if (import.meta.env.DEV) {
      console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`, {
        data: config.data,
        params: config.params,
      });
    }

    return config;
  },
  (error) => {
    console.error('Request interceptor error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor
apiClient.interceptors.response.use(
  (response) => {
    // Calculate request duration
    const duration = new Date() - response.config.metadata.startTime;

    // Log response in development
    if (import.meta.env.DEV) {
      console.log(`✅ API Response: ${response.config.method?.toUpperCase()} ${response.config.url} (${duration}ms)`, {
        status: response.status,
        data: response.data,
      });
    }

    return response;
  },
  (error) => {
    // Calculate request duration
    const duration = error.config?.metadata ? new Date() - error.config.metadata.startTime : 0;

    // Log error in development
    if (import.meta.env.DEV) {
      console.error(`❌ API Error: ${error.config?.method?.toUpperCase()} ${error.config?.url} (${duration}ms)`, {
        status: error.response?.status,
        data: error.response?.data,
        message: error.message,
      });
    }

    // Handle specific error cases
    if (error.response) {
      const { status, data } = error.response;

      switch (status) {
        case 401:
          // Unauthorized - clear token and redirect to login
          clearAuthToken();
          if (window.location.pathname !== '/login') {
            window.location.href = '/login';
          }
          break;

        case 403:
          // Forbidden - show permission denied message
          console.warn('Access denied:', data?.message || 'Insufficient permissions');
          break;

        case 429: {
          // Rate limit exceeded
          const retryAfter = error.response.headers['retry-after'];
          console.warn(`Rate limit exceeded. Retry after ${retryAfter} seconds`);
          break;
        }

        case 500:
          // Server error
          console.error('Server error:', data?.message || 'Internal server error');
          break;

        default:
          console.error('API error:', data?.message || error.message);
      }

      // Return structured error
      return Promise.reject({
        status,
        message: data?.error || data?.message || error.message,
        details: data?.details,
        errorCode: data?.error_code,
        originalError: error,
      });
    } else if (error.request) {
      // Network error
      console.error('Network error:', error.message);
      return Promise.reject({
        status: 0,
        message: 'Network error. Please check your connection.',
        originalError: error,
      });
    } else {
      // Other error
      console.error('Request setup error:', error.message);
      return Promise.reject({
        status: 0,
        message: error.message,
        originalError: error,
      });
    }
  }
);

// API methods
export const api = {
  // Authentication
  auth: {
    login: (credentials) => apiClient.post('/auth/login', credentials),
    register: (userData) => apiClient.post('/auth/register', userData),
    logout: () => apiClient.post('/auth/logout'),
    refreshToken: () => apiClient.post('/auth/refresh'),
    verifyCode: (data) => apiClient.post('/auth/verify-code', data),
    requestCode: (phoneNumber) => apiClient.post('/auth/request-code', { phone_number: phoneNumber }),
    verify2FA: (data) => apiClient.post('/auth/verify-2fa', data),
  },

  // Messages
  messages: {
    getAll: (params) => apiClient.get('/messages', { params }),
    getById: (id) => apiClient.get(`/messages/${id}`),
    create: (data) => apiClient.post('/messages', data),
    update: (id, data) => apiClient.put(`/messages/${id}`, data),
    delete: (id) => apiClient.delete(`/messages/${id}`),
    send: (id, data) => apiClient.post(`/messages/${id}/send`, data),
    preview: (data) => apiClient.post('/messages/preview', data),
  },

  // Groups
  groups: {
    getAll: (params) => apiClient.get('/groups', { params }),
    getById: (id) => apiClient.get(`/groups/${id}`),
    create: (data) => apiClient.post('/groups', data),
    update: (id, data) => apiClient.put(`/groups/${id}`, data),
    delete: (id) => apiClient.delete(`/groups/${id}`),
    sync: () => apiClient.post('/groups/sync'),
    validate: (groupId) => apiClient.post(`/groups/${groupId}/validate`),
  },

  // Scheduler
  scheduler: {
    getJobs: (params) => apiClient.get('/scheduler/jobs', { params }),
    getJob: (id) => apiClient.get(`/scheduler/jobs/${id}`),
    createJob: (data) => apiClient.post('/scheduler/jobs', data),
    updateJob: (id, data) => apiClient.put(`/scheduler/jobs/${id}`, data),
    deleteJob: (id) => apiClient.delete(`/scheduler/jobs/${id}`),
    pauseJob: (id) => apiClient.post(`/scheduler/jobs/${id}/pause`),
    resumeJob: (id) => apiClient.post(`/scheduler/jobs/${id}/resume`),
    getStatus: () => apiClient.get('/scheduler/status'),
    getLogs: (params) => apiClient.get('/scheduler/logs', { params }),
  },

  // Blacklist
  blacklist: {
    getAll: (params) => apiClient.get('/blacklist', { params }),
    add: (data) => apiClient.post('/blacklist', data),
    remove: (id) => apiClient.delete(`/blacklist/${id}`),
    check: (identifier) => apiClient.post('/blacklist/check', { identifier }),
    import: (data) => apiClient.post('/blacklist/import', data),
    export: () => apiClient.get('/blacklist/export'),
  },

  // Settings
  settings: {
    get: () => apiClient.get('/settings'),
    update: (data) => apiClient.put('/settings', data),
    reset: () => apiClient.post('/settings/reset'),
    export: () => apiClient.get('/settings/export'),
    import: (data) => apiClient.post('/settings/import', data),
  },

  // Dashboard/Stats
  dashboard: {
    getStats: () => apiClient.get('/dashboard/stats'),
    getActivity: (params) => apiClient.get('/dashboard/activity', { params }),
    getCharts: (params) => apiClient.get('/dashboard/charts', { params }),
  },

  // Health check
  health: () => apiClient.get('/health', { baseURL: API_BASE_URL }),
};

// Utility functions
export const createFormData = (data) => {
  const formData = new FormData();
  Object.keys(data).forEach(key => {
    if (data[key] !== null && data[key] !== undefined) {
      if (data[key] instanceof File) {
        formData.append(key, data[key]);
      } else if (Array.isArray(data[key])) {
        data[key].forEach(item => formData.append(key, item));
      } else {
        formData.append(key, String(data[key]));
      }
    }
  });
  return formData;
};

export const downloadFile = async (url, filename) => {
  try {
    const response = await apiClient.get(url, { responseType: 'blob' });
    const blob = new Blob([response.data]);
    const downloadUrl = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(downloadUrl);
  } catch (error) {
    console.error('Download failed:', error);
    throw error;
  }
};

// Export token management functions
export { getAuthToken, setAuthToken, clearAuthToken };

// Export the configured axios instance
export default apiClient;

