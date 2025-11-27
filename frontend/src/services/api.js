import axios from 'axios';

// Use relative URL in production, absolute URL in development
const API_BASE_URL = process.env.NODE_ENV === 'production'
  ? '/api'
  : 'http://127.0.0.1:8000/api';

// Request retry configuration
const RETRY_CONFIG = {
  retries: 3,
  retryDelay: 1000,
  retryCondition: (error) => {
    return error.code === 'NETWORK_ERROR' ||
      (error.response && error.response.status >= 500);
  }
};

// Create axios instance with enhanced configuration
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 seconds timeout
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request counter for loading states
let activeRequests = 0;
const requestListeners = new Set();

// Add request listener
const addRequestListener = (listener) => {
  requestListeners.add(listener);
  return () => requestListeners.delete(listener);
};

// Notify listeners about loading state changes
const notifyListeners = (isLoading) => {
  requestListeners.forEach(listener => listener(isLoading));
};

// Request interceptor with enhanced features
api.interceptors.request.use(
  (config) => {
    // Add auth token
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    // Track active requests
    activeRequests++;
    if (activeRequests === 1) {
      notifyListeners(true);
    }

    // Add request timestamp for debugging
    config.metadata = { startTime: new Date() };

    return config;
  },
  (error) => {
    activeRequests = Math.max(0, activeRequests - 1);
    if (activeRequests === 0) {
      notifyListeners(false);
    }
    return Promise.reject(error);
  }
);

// Response interceptor with enhanced error handling
api.interceptors.response.use(
  (response) => {
    // Track request completion
    activeRequests = Math.max(0, activeRequests - 1);
    if (activeRequests === 0) {
      notifyListeners(false);
    }

    // Log response time in development
    if (process.env.NODE_ENV === 'development' && response.config.metadata) {
      const duration = new Date() - response.config.metadata.startTime;
      console.log(`API Request: ${response.config.method?.toUpperCase()} ${response.config.url} - ${duration}ms`);
    }

    return response;
  },
  async (error) => {
    // Track request completion
    activeRequests = Math.max(0, activeRequests - 1);
    if (activeRequests === 0) {
      notifyListeners(false);
    }

    const originalRequest = error.config;

    // Handle authentication errors with token refresh
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        // Try to refresh the token
        const refreshTokenValue = localStorage.getItem('refresh_token');
        if (refreshTokenValue) {
          const response = await api.post('/auth/refresh/', {
            refresh: refreshTokenValue
          });

          const { access, refresh } = response.data;
          setAuthToken(access);

          if (refresh) {
            localStorage.setItem('refresh_token', refresh);
          }

          // Retry the original request with new token
          originalRequest.headers.Authorization = `Bearer ${access}`;
          return api(originalRequest);
        }
      } catch (refreshError) {
        // Refresh failed, clear auth data and redirect
        console.warn('Token refresh failed:', refreshError);
      }

      // Clear auth data
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      delete api.defaults.headers.common['Authorization'];

      // Redirect to login if not already there
      if (window.location.pathname !== '/login') {
        window.location.href = '/login';
      }

      return Promise.reject(error);
    }

    // Handle network errors with retry logic
    if (RETRY_CONFIG.retryCondition(error) &&
      (!originalRequest._retryCount || originalRequest._retryCount < RETRY_CONFIG.retries)) {

      originalRequest._retryCount = (originalRequest._retryCount || 0) + 1;

      // Exponential backoff
      const delay = RETRY_CONFIG.retryDelay * Math.pow(2, originalRequest._retryCount - 1);

      await new Promise(resolve => setTimeout(resolve, delay));

      return api(originalRequest);
    }

    // Enhanced error logging
    if (process.env.NODE_ENV === 'development') {
      console.error('API Error:', {
        url: error.config?.url,
        method: error.config?.method,
        status: error.response?.status,
        data: error.response?.data,
        message: error.message
      });
    }

    return Promise.reject(error);
  }
);

// Function to set the authorization header
const setAuthToken = (token) => {
  if (token) {
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    localStorage.setItem('access_token', token);
  } else {
    delete api.defaults.headers.common['Authorization'];
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  }
};

// Helper function to check if request is loading
const isLoading = () => activeRequests > 0;

// Enhanced error handling wrapper
const handleApiCall = async (apiCall, errorMessage = 'API call failed') => {
  try {
    const response = await apiCall();
    return response.data;
  } catch (error) {
    // Enhanced error processing
    const processedError = {
      message: error.response?.data?.detail ||
        error.response?.data?.message ||
        error.message ||
        errorMessage,
      status: error.response?.status,
      data: error.response?.data,
      originalError: error
    };

    throw processedError;
  }
};

// Authentication functions
const loginUser = async (credentials) => {
  return handleApiCall(
    () => api.post('/auth/login/', credentials),
    'Login failed'
  ).then(data => {
    setAuthToken(data.access);
    // Store refresh token
    localStorage.setItem('refresh_token', data.refresh);
    return data;
  });
};

const registerUser = async (userData) => {
  return handleApiCall(
    () => api.post('/auth/register/', userData),
    'Registration failed'
  ).then(data => {
    if (data.tokens) {
      setAuthToken(data.tokens.access);
      localStorage.setItem('refresh_token', data.tokens.refresh);
    }
    return data;
  });
};

// Token refresh function
const refreshToken = async () => {
  const refresh = localStorage.getItem('refresh_token');
  if (!refresh) {
    throw new Error('No refresh token available');
  }

  return handleApiCall(
    () => api.post('/auth/refresh/', { refresh }),
    'Token refresh failed'
  ).then(data => {
    setAuthToken(data.access);
    if (data.refresh) {
      localStorage.setItem('refresh_token', data.refresh);
    }
    return data;
  });
};

// Logout function
const logoutUser = async () => {
  const refresh = localStorage.getItem('refresh_token');

  try {
    if (refresh) {
      await handleApiCall(
        () => api.post('/auth/logout/', { refresh_token: refresh }),
        'Logout failed'
      );
    }
  } catch (error) {
    // Continue with logout even if server call fails
    console.warn('Logout API call failed:', error);
  } finally {
    // Clear local storage
    setAuthToken(null);
    localStorage.removeItem('refresh_token');
  }
};

// Screen Type functions
const fetchScreenTypes = async (params = {}) => {
  return handleApiCall(
    () => api.get('/screentypes/', { params }),
    'Failed to fetch screen types'
  );
};

const getScreenTypes = fetchScreenTypes; // Backward compatibility

// Visualization Request functions
const fetchVisualizationRequests = async (params = {}) => {
  return handleApiCall(
    () => api.get('/visualizations/', { params }),
    'Failed to fetch visualization requests'
  );
};

const getVisualizationRequests = fetchVisualizationRequests; // Backward compatibility

const createVisualizationRequest = async (formData) => {
  return handleApiCall(
    () => api.post('/visualizations/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    }),
    'Failed to create visualization request'
  );
};

const getVisualizationRequestById = async (id) => {
  return handleApiCall(
    () => api.get(`/visualizations/${id}/`),
    'Failed to fetch visualization request'
  );
};

const updateVisualizationRequest = async (id, data) => {
  return handleApiCall(
    () => api.put(`/visualizations/${id}/`, data),
    'Failed to update visualization request'
  );
};

const deleteVisualizationRequest = async (id) => {
  return handleApiCall(
    () => api.delete(`/visualizations/${id}/`),
    'Failed to delete visualization request'
  );
};

const retryVisualizationRequest = async (id) => {
  return handleApiCall(
    () => api.post(`/visualizations/${id}/retry/`),
    'Failed to retry visualization request'
  );
};

const regenerateVisualizationRequest = async (id) => {
  return handleApiCall(
    () => api.post(`/visualizations/${id}/regenerate/`),
    'Failed to regenerate visualization request'
  );
};

// Generated Images functions
const fetchGeneratedImages = async (params = {}) => {
  return handleApiCall(
    () => api.get('/generated-images/', { params }),
    'Failed to fetch generated images'
  );
};

const getGeneratedImageById = async (id) => {
  return handleApiCall(
    () => api.get(`/generated-images/${id}/`),
    'Failed to fetch generated image'
  );
};

// User Profile functions
const fetchUserProfile = async () => {
  return handleApiCall(
    () => api.get('/profile/'),
    'Failed to fetch user profile'
  );
};

const updateUserProfile = async (data) => {
  return handleApiCall(
    () => api.put('/profile/', data),
    'Failed to update user profile'
  );
};

// Statistics functions
const fetchUserStats = async () => {
  return handleApiCall(
    () => api.get('/visualizations/stats/'),
    'Failed to fetch user statistics'
  );
};

// Initialize auth token from localStorage on page load
const initializeAuth = () => {
  const token = localStorage.getItem('access_token');
  if (token) {
    setAuthToken(token);
  }
};

// Health check function
const healthCheck = async () => {
  return handleApiCall(
    () => api.get('/health/'),
    'Health check failed'
  );
};

// Export all functions
export {
  // Authentication
  loginUser,
  registerUser,
  logoutUser,
  refreshToken,
  setAuthToken,
  initializeAuth,

  // Screen Types
  fetchScreenTypes,
  getScreenTypes, // Backward compatibility

  // Visualization Requests
  fetchVisualizationRequests,
  getVisualizationRequests, // Backward compatibility
  createVisualizationRequest,
  getVisualizationRequestById,
  updateVisualizationRequest,
  deleteVisualizationRequest,
  retryVisualizationRequest,
  regenerateVisualizationRequest,

  // Generated Images
  fetchGeneratedImages,
  getGeneratedImageById,

  // User Profile
  fetchUserProfile,
  updateUserProfile,

  // Statistics
  fetchUserStats,

  // Utilities
  healthCheck,
  addRequestListener,
  isLoading
};
