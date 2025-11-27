import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import { loginUser, registerUser, logoutUser, refreshToken, setAuthToken } from '../services/api';

// Helper function to safely access localStorage
const safeLocalStorage = {
  getItem: (key) => {
    try {
      return localStorage.getItem(key);
    } catch {
      return null;
    }
  },
  setItem: (key, value) => {
    try {
      localStorage.setItem(key, value);
    } catch {
      // Silently fail if localStorage is not available
    }
  },
  removeItem: (key) => {
    try {
      localStorage.removeItem(key);
    } catch {
      // Silently fail if localStorage is not available
    }
  }
};

// Initial state
const initialState = {
  user: null,
  token: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,
  lastLoginTime: null,
  loginAttempts: 0,
  isLocked: false
};

const useAuthStore = create(
  persist(
    (set, get) => ({
      ...initialState,

      // Actions
      login: async (credentials) => {
        const state = get();

        // Check if account is locked
        if (state.isLocked) {
          const lockTime = 15 * 60 * 1000; // 15 minutes
          const timeSinceLastAttempt = Date.now() - state.lastLoginTime;
          if (timeSinceLastAttempt < lockTime) {
            const remainingTime = Math.ceil((lockTime - timeSinceLastAttempt) / 60000);
            throw new Error(`Account locked. Try again in ${remainingTime} minutes.`);
          } else {
            // Unlock account after timeout
            set({ isLocked: false, loginAttempts: 0 });
          }
        }

        set({ isLoading: true, error: null });

        try {
          const response = await loginUser(credentials);

          // Set auth token for future requests
          setAuthToken(response.access);

          set({
            isAuthenticated: true,
            token: response.access,
            isLoading: false,
            user: {
              username: credentials.username,
              // Add more user data from response if available
              ...response.user
            },
            error: null,
            lastLoginTime: Date.now(),
            loginAttempts: 0,
            isLocked: false
          });

          return response;
        } catch (error) {
          const newAttempts = state.loginAttempts + 1;
          const shouldLock = newAttempts >= 5;

          set({
            isLoading: false,
            error: error.response?.data?.detail || error.message || 'Login failed',
            loginAttempts: newAttempts,
            isLocked: shouldLock,
            lastLoginTime: Date.now()
          });

          throw error;
        }
      },

      register: async (userData) => {
        set({ isLoading: true, error: null });

        try {
          const response = await registerUser(userData);
          set({
            isLoading: false,
            error: null
          });
          return response;
        } catch (error) {
          const errorMessage = error.response?.data?.detail ||
                              error.response?.data?.message ||
                              error.message ||
                              'Registration failed';

          set({
            isLoading: false,
            error: errorMessage
          });
          throw error;
        }
      },

      logout: async () => {
        try {
          await logoutUser();
        } catch (error) {
          console.warn('Logout API call failed:', error);
        } finally {
          // Clear auth token from API service
          setAuthToken(null);

          // Reset state to initial values
          set({
            ...initialState
          });
        }
      },

      // Clear error state
      clearError: () => {
        set({ error: null });
      },

      // Update user profile
      updateUser: (userData) => {
        set(state => ({
          user: { ...state.user, ...userData }
        }));
      },

      // Check if token is expired (basic check)
      isTokenExpired: () => {
        const state = get();
        if (!state.token) return true;

        try {
          // Basic JWT expiration check
          const payload = JSON.parse(atob(state.token.split('.')[1]));
          const currentTime = Date.now() / 1000;
          return payload.exp < currentTime;
        } catch {
          return true;
        }
      },

      // Initialize auth state from storage
      initializeAuth: () => {
        const state = get();

        if (state.token && !state.isTokenExpired()) {
          setAuthToken(state.token);
          set({ isAuthenticated: true });
        } else {
          // Token is expired or invalid, clear auth
          set({ ...initialState });
        }
      },

      // Refresh authentication status
      refreshAuth: async () => {
        const state = get();

        if (!state.token || state.isTokenExpired()) {
          try {
            const data = await refreshToken();
            set({
              token: data.access,
              isAuthenticated: true,
              error: null
            });
            return true;
          } catch (error) {
            set({ ...initialState });
            return false;
          }
        }

        try {
          setAuthToken(state.token);
          return true;
        } catch {
          set({ ...initialState });
          return false;
        }
      }
    }),
    {
      name: 'auth-storage',
      storage: createJSONStorage(() => safeLocalStorage),
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        isAuthenticated: state.isAuthenticated,
        lastLoginTime: state.lastLoginTime,
        loginAttempts: state.loginAttempts,
        isLocked: state.isLocked
      }),
      onRehydrateStorage: () => (state) => {
        // Initialize auth when store is rehydrated
        if (state) {
          state.initializeAuth();
        }
      }
    }
  )
);

export default useAuthStore;
