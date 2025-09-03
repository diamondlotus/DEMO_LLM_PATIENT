import axios from 'axios';

// Create axios instance
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || '/api',
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

// Response interceptor to handle auth errors
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

// Auth API
export const authAPI = {
  // Backend expects OAuth2PasswordRequestForm at /auth/token with form-encoded fields
  login: (identifier, password) => {
    const params = new URLSearchParams();
    params.append('username', identifier);
    params.append('password', password);
    return api.post('/auth/token', params, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
  },

  // Not implemented in backend (placeholder for future)
  register: (userData) => api.post('/auth/register', userData),

  // Correct path in backend is /auth/users/me
  getCurrentUser: () => api.get('/auth/users/me'),

  // Not implemented in backend (placeholder for future)
  refreshToken: () => api.post('/auth/refresh'),

  // Not implemented in backend (placeholder for future)
  changePassword: (oldPassword, newPassword) =>
    api.post('/auth/change-password', { old_password: oldPassword, new_password: newPassword }),
};

// Patients API
export const patientsAPI = {
  getAll: (params = {}) => 
    api.get('/clinic/patients', { params }),
  
  getById: (id) => 
    api.get(`/clinic/patients/${id}`),
  
  create: (patientData) => 
    api.post('/clinic/patients', patientData),
  
  update: (id, patientData) => 
    api.put(`/clinic/patients/${id}`, patientData),
  
  delete: (id) => 
    api.delete(`/clinic/patients/${id}`),
  
  search: (query) => 
    api.get('/clinic/patients/search', { params: { q: query } }),
};

// Appointments API
export const appointmentsAPI = {
  getAll: (params = {}) => 
    api.get('/clinic/appointments', { params }),
  
  getById: (id) => 
    api.get(`/clinic/appointments/${id}`),
  
  create: (appointmentData) => 
    api.post('/clinic/appointments', appointmentData),
  
  update: (id, appointmentData) => 
    api.put(`/clinic/appointments/${id}`, appointmentData),
  
  delete: (id) => 
    api.delete(`/clinic/appointments/${id}`),
  
  getByPatient: (patientId) => 
    api.get(`/clinic/appointments/patient/${patientId}`),
  
  getByDoctor: (doctorId) => 
    api.get(`/clinic/appointments/doctor/${doctorId}`),
  
  getUpcoming: () => 
    api.get('/clinic/appointments/upcoming'),
  
  getToday: () => 
    api.get('/clinic/appointments/today'),
};

// Doctors API
export const doctorsAPI = {
  getAll: (params = {}) => 
    api.get('/clinic/doctors', { params }),
  
  getById: (id) => 
    api.get(`/clinic/doctors/${id}`),
  
  create: (doctorData) => 
    api.post('/clinic/doctors', doctorData),
  
  update: (id, doctorData) => 
    api.put(`/clinic/doctors/${id}`, doctorData),
  
  delete: (id) => 
    api.delete(`/clinic/doctors/${id}`),
  
  getSchedule: (id, date) => 
    api.get(`/clinic/doctors/${id}/schedule`, { params: { date } }),
  
  updateSchedule: (id, scheduleData) => 
    api.put(`/clinic/doctors/${id}/schedule`, scheduleData),
};

// AI Processing API
export const aiAPI = {
  processNote: (noteData) => {
    console.log('Making AI API call to:', '/ai/process-note/simple');
    console.log('Full URL will be:', api.defaults.baseURL + '/ai/process-note/simple');
    return api.post('/ai/process-note/simple', noteData);
  },

  learnAndUpdate: (learningData) => {
    console.log('Making AI learning call to:', '/ai/learn-and-update');
    return api.post('/ai/learn-and-update', learningData);
  },

  getProcessingHistory: (params = {}) =>
    api.get('/ai/processing-history', { params }),

  getProcessingById: (id) =>
    api.get(`/ai/processing/${id}`),

  // AI Learning endpoints
  uploadFile: (formData) =>
    api.post('/ai/upload-file', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    }),

  uploadText: (textData) =>
    api.post('/ai/upload-text', textData),

  loadDemoData: () =>
    api.post('/ai/load-demo-data'),

  getUploadedContent: () =>
    api.get('/ai/uploaded-content'),

  getLearningStatistics: () =>
    api.get('/ai/learning-statistics'),

  deleteUploadedContent: (contentId) =>
    api.delete(`/ai/uploaded-content/${contentId}`),
};

// Dashboard API
export const dashboardAPI = {
  getStats: () => 
    api.get('/clinic/dashboard/stats'),
  
  getRecentAppointments: () => 
    api.get('/clinic/dashboard/recent-appointments'),
  
  getUpcomingAppointments: () => 
    api.get('/clinic/dashboard/upcoming-appointments'),
  
  getPatientStats: () => 
    api.get('/clinic/dashboard/patient-stats'),
  
  getRevenueStats: () => 
    api.get('/clinic/dashboard/revenue-stats'),
};

// Users API (for admin)
export const usersAPI = {
  getAll: (params = {}) => 
    api.get('/auth/users', { params }),
  
  getById: (id) => 
    api.get(`/auth/users/${id}`),
  
  create: (userData) => 
    api.post('/auth/users', userData),
  
  update: (id, userData) => 
    api.put(`/auth/users/${id}`, userData),
  
  delete: (id) => 
    api.delete(`/auth/users/${id}`),
  
  updateRole: (id, role) => 
    api.put(`/auth/users/${id}/role`, { role }),
  
  updatePermissions: (id, permissions) => 
    api.put(`/auth/users/${id}/permissions`, { permissions }),
};

// Settings API
export const settingsAPI = {
  getClinicSettings: () => 
    api.get('/clinic/settings'),
  
  updateClinicSettings: (settings) => 
    api.put('/clinic/settings', settings),
  
  getSystemSettings: () => 
    api.get('/auth/settings'),
  
  updateSystemSettings: (settings) => 
    api.put('/auth/settings', settings),
};

export default api;
