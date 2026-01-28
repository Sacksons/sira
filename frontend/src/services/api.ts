import axios, { AxiosInstance, AxiosError, InternalAxiosRequestConfig } from 'axios'
import { useAuthStore } from '../stores/authStore'

const API_BASE_URL = import.meta.env.VITE_API_URL || ''

export const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add auth token
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = useAuthStore.getState().token
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      useAuthStore.getState().logout()
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// API service functions
export const authApi = {
  login: (username: string, password: string) =>
    api.post('/api/v1/auth/token', new URLSearchParams({ username, password }), {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    }),
  getCurrentUser: () => api.get('/api/v1/auth/me'),
  changePassword: (currentPassword: string, newPassword: string) =>
    api.post('/api/v1/auth/change-password', {
      current_password: currentPassword,
      new_password: newPassword,
    }),
}

export const alertsApi = {
  getAll: (params?: Record<string, any>) => api.get('/api/v1/alerts/', { params }),
  getById: (id: number) => api.get(`/api/v1/alerts/${id}`),
  create: (data: any) => api.post('/api/v1/alerts/', data),
  update: (id: number, data: any) => api.put(`/api/v1/alerts/${id}`, data),
  acknowledge: (id: number) => api.post(`/api/v1/alerts/${id}/acknowledge`),
  resolve: (id: number, notes: string) =>
    api.post(`/api/v1/alerts/${id}/resolve`, { resolution_notes: notes }),
  getStats: () => api.get('/api/v1/alerts/stats'),
}

export const casesApi = {
  getAll: (params?: Record<string, any>) => api.get('/api/v1/cases/', { params }),
  getById: (id: number) => api.get(`/api/v1/cases/${id}`),
  create: (data: any) => api.post('/api/v1/cases/', data),
  update: (id: number, data: any) => api.put(`/api/v1/cases/${id}`, data),
  close: (id: number, data: any) => api.post(`/api/v1/cases/${id}/close`, data),
  export: (id: number, format: 'json' | 'pdf' = 'json') =>
    api.get(`/api/v1/cases/${id}/export`, { params: { format } }),
  getStats: () => api.get('/api/v1/cases/stats'),
}

export const movementsApi = {
  getAll: (params?: Record<string, any>) => api.get('/api/v1/movements/', { params }),
  getById: (id: number) => api.get(`/api/v1/movements/${id}`),
  create: (data: any) => api.post('/api/v1/movements/', data),
  update: (id: number, data: any) => api.put(`/api/v1/movements/${id}`, data),
  delete: (id: number) => api.delete(`/api/v1/movements/${id}`),
}

export const usersApi = {
  getAll: (params?: Record<string, any>) => api.get('/api/v1/users/', { params }),
  getById: (id: number) => api.get(`/api/v1/users/${id}`),
  create: (data: any) => api.post('/api/v1/users/', data),
  update: (id: number, data: any) => api.put(`/api/v1/users/${id}`, data),
  delete: (id: number) => api.delete(`/api/v1/users/${id}`),
  activate: (id: number) => api.post(`/api/v1/users/${id}/activate`),
}

export const reportsApi = {
  getDashboard: () => api.get('/api/v1/reports/dashboard'),
  getAlertsSummary: (params?: Record<string, any>) =>
    api.get('/api/v1/reports/alerts/summary', { params }),
  getActivity: (days: number = 7) =>
    api.get('/api/v1/reports/activity', { params: { days } }),
}

export const notificationsApi = {
  getAll: (params?: Record<string, any>) => api.get('/api/v1/notifications/', { params }),
  getUnreadCount: () => api.get('/api/v1/notifications/unread-count'),
  markAsRead: (id: number) => api.post(`/api/v1/notifications/${id}/read`),
  markAllAsRead: () => api.post('/api/v1/notifications/read-all'),
  getPreferences: () => api.get('/api/v1/notifications/preferences'),
  updatePreferences: (data: any) => api.put('/api/v1/notifications/preferences', data),
}
