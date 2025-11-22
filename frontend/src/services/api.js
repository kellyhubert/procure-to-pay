import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        const response = await axios.post(`${API_BASE_URL}/token/refresh/`, {
          refresh: refreshToken,
        });

        const { access } = response.data;
        localStorage.setItem('access_token', access);

        originalRequest.headers.Authorization = `Bearer ${access}`;
        return api(originalRequest);
      } catch (refreshError) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  login: (username, password) =>
    api.post('/token/', { username, password }),

  register: (userData) =>
    api.post('/users/register/', userData),

  getCurrentUser: () =>
    api.get('/users/me/'),
};

// Purchase Requests API
export const requestsAPI = {
  list: (params) =>
    api.get('/requests/', { params }),

  get: (id) =>
    api.get(`/requests/${id}/`),

  create: (data) => {
    const formData = new FormData();
    Object.keys(data).forEach(key => {
      if (data[key] !== null && data[key] !== undefined) {
        formData.append(key, data[key]);
      }
    });
    return api.post('/requests/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },

  update: (id, data) =>
    api.put(`/requests/${id}/`, data),

  approve: (id, comments) =>
    api.patch(`/requests/${id}/approve/`, { approved: true, comments }),

  reject: (id, comments) =>
    api.patch(`/requests/${id}/reject/`, { approved: false, comments }),

  submitReceipt: (id, receiptFile) => {
    const formData = new FormData();
    formData.append('receipt', receiptFile);
    return api.post(`/requests/${id}/submit_receipt/`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
};

// Approvals API
export const approvalsAPI = {
  list: () =>
    api.get('/approvals/'),
};

export default api;
