import { renderHook, act } from '@testing-library/react';
import useAuthStore from '../authStore';
import * as api from '../../services/api';

// Mock the API module
jest.mock('../../services/api');

describe('Auth Store', () => {
  beforeEach(() => {
    // Clear the store state before each test
    useAuthStore.getState().logout();
    jest.clearAllMocks();
    
    // Clear localStorage
    localStorage.clear();
  });

  describe('initial state', () => {
    it('has correct initial state', () => {
      const { result } = renderHook(() => useAuthStore());
      
      expect(result.current.user).toBeNull();
      expect(result.current.token).toBeNull();
      expect(result.current.isAuthenticated).toBe(false);
      expect(result.current.isLoading).toBe(false);
      expect(result.current.error).toBeNull();
      expect(result.current.loginAttempts).toBe(0);
      expect(result.current.isLocked).toBe(false);
    });
  });

  describe('login', () => {
    it('successfully logs in user', async () => {
      const mockResponse = {
        access: 'mock-token',
        user: { id: 1, username: 'testuser' }
      };
      
      api.loginUser.mockResolvedValue(mockResponse);
      api.setAuthToken.mockImplementation(() => {});
      
      const { result } = renderHook(() => useAuthStore());
      
      await act(async () => {
        await result.current.login({ username: 'testuser', password: 'password' });
      });
      
      expect(result.current.isAuthenticated).toBe(true);
      expect(result.current.token).toBe('mock-token');
      expect(result.current.user.username).toBe('testuser');
      expect(result.current.isLoading).toBe(false);
      expect(result.current.error).toBeNull();
      expect(result.current.loginAttempts).toBe(0);
      expect(api.setAuthToken).toHaveBeenCalledWith('mock-token');
    });

    it('handles login failure', async () => {
      const mockError = {
        response: { data: { detail: 'Invalid credentials' } }
      };
      
      api.loginUser.mockRejectedValue(mockError);
      
      const { result } = renderHook(() => useAuthStore());
      
      await act(async () => {
        try {
          await result.current.login({ username: 'testuser', password: 'wrong' });
        } catch (error) {
          // Expected to throw
        }
      });
      
      expect(result.current.isAuthenticated).toBe(false);
      expect(result.current.token).toBeNull();
      expect(result.current.user).toBeNull();
      expect(result.current.isLoading).toBe(false);
      expect(result.current.error).toBe('Invalid credentials');
      expect(result.current.loginAttempts).toBe(1);
    });

    it('locks account after 5 failed attempts', async () => {
      const mockError = {
        response: { data: { detail: 'Invalid credentials' } }
      };
      
      api.loginUser.mockRejectedValue(mockError);
      
      const { result } = renderHook(() => useAuthStore());
      
      // Simulate 5 failed login attempts
      for (let i = 0; i < 5; i++) {
        await act(async () => {
          try {
            await result.current.login({ username: 'testuser', password: 'wrong' });
          } catch (error) {
            // Expected to throw
          }
        });
      }
      
      expect(result.current.isLocked).toBe(true);
      expect(result.current.loginAttempts).toBe(5);
      
      // Try to login again when locked
      await act(async () => {
        try {
          await result.current.login({ username: 'testuser', password: 'password' });
        } catch (error) {
          expect(error.message).toContain('Account locked');
        }
      });
    });
  });

  describe('register', () => {
    it('successfully registers user', async () => {
      const mockResponse = { message: 'User created successfully' };
      api.registerUser.mockResolvedValue(mockResponse);
      
      const { result } = renderHook(() => useAuthStore());
      
      const userData = {
        username: 'newuser',
        email: 'new@example.com',
        password: 'password123'
      };
      
      await act(async () => {
        await result.current.register(userData);
      });
      
      expect(result.current.isLoading).toBe(false);
      expect(result.current.error).toBeNull();
      expect(api.registerUser).toHaveBeenCalledWith(userData);
    });

    it('handles registration failure', async () => {
      const mockError = {
        response: { data: { detail: 'Username already exists' } }
      };
      
      api.registerUser.mockRejectedValue(mockError);
      
      const { result } = renderHook(() => useAuthStore());
      
      await act(async () => {
        try {
          await result.current.register({
            username: 'existing',
            email: 'test@example.com',
            password: 'password'
          });
        } catch (error) {
          // Expected to throw
        }
      });
      
      expect(result.current.isLoading).toBe(false);
      expect(result.current.error).toBe('Username already exists');
    });
  });

  describe('logout', () => {
    it('clears user data on logout', async () => {
      // First login
      const mockResponse = {
        access: 'mock-token',
        user: { id: 1, username: 'testuser' }
      };
      
      api.loginUser.mockResolvedValue(mockResponse);
      api.setAuthToken.mockImplementation(() => {});
      
      const { result } = renderHook(() => useAuthStore());
      
      await act(async () => {
        await result.current.login({ username: 'testuser', password: 'password' });
      });
      
      // Then logout
      act(() => {
        result.current.logout();
      });
      
      expect(result.current.isAuthenticated).toBe(false);
      expect(result.current.token).toBeNull();
      expect(result.current.user).toBeNull();
      expect(result.current.error).toBeNull();
      expect(api.setAuthToken).toHaveBeenLastCalledWith(null);
    });
  });

  describe('utility methods', () => {
    it('clears error', () => {
      const { result } = renderHook(() => useAuthStore());
      
      // Set an error first
      act(() => {
        result.current.login({ username: 'test', password: 'wrong' }).catch(() => {});
      });
      
      act(() => {
        result.current.clearError();
      });
      
      expect(result.current.error).toBeNull();
    });

    it('updates user data', () => {
      const { result } = renderHook(() => useAuthStore());
      
      // Set initial user
      act(() => {
        useAuthStore.setState({
          user: { id: 1, username: 'testuser', email: 'old@example.com' }
        });
      });
      
      act(() => {
        result.current.updateUser({ email: 'new@example.com' });
      });
      
      expect(result.current.user.email).toBe('new@example.com');
      expect(result.current.user.username).toBe('testuser'); // Should preserve other fields
    });

    it('checks if token is expired', () => {
      const { result } = renderHook(() => useAuthStore());
      
      // Test with no token
      expect(result.current.isTokenExpired()).toBe(true);
      
      // Test with valid token (mock JWT)
      const validToken = 'header.' + btoa(JSON.stringify({ exp: Date.now() / 1000 + 3600 })) + '.signature';
      act(() => {
        useAuthStore.setState({ token: validToken });
      });
      
      expect(result.current.isTokenExpired()).toBe(false);
      
      // Test with expired token
      const expiredToken = 'header.' + btoa(JSON.stringify({ exp: Date.now() / 1000 - 3600 })) + '.signature';
      act(() => {
        useAuthStore.setState({ token: expiredToken });
      });
      
      expect(result.current.isTokenExpired()).toBe(true);
    });
  });
});
