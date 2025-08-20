import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api/v1';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Candidate API service
export const candidateAPI = {
  // Get all candidates with filters
  getAll: async (filters = {}) => {
    const response = await api.get('/candidates', { params: filters });
    return response.data;
  },

  // Get single candidate
  getById: async (id) => {
    const response = await api.get(`/candidates/${id}`);
    return response.data;
  },

  // Update candidate status
  updateStatus: async (id, status) => {
    const response = await api.patch(`/candidates/${id}/status`, { status });
    return response.data;
  },

  // Get candidate statistics
  getStats: async () => {
    const response = await api.get('/candidates/stats/overview');
    return response.data;
  },

  // Create candidate (for testing)
  create: async (candidateData) => {
    const response = await api.post('/candidates', candidateData);
    return response.data;
  }
};

// Log API service
export const logAPI = {
  // Get all logs with filters
  getAll: async (filters = {}) => {
    const response = await api.get('/logs', { params: filters });
    return response.data;
  }
};

// Auth API service
export const authAPI = {
  // Login
  login: async (credentials) => {
    const response = await api.post('/auth/login', credentials);
    return response.data;
  },

  // Register
  register: async (userData) => {
    const response = await api.post('/auth/register', userData);
    return response.data;
  }
};

export default api;
