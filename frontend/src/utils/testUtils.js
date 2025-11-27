import React from 'react';
import { render } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';

// Mock store provider for testing
const MockStoreProvider = ({ children, initialState = {} }) => {
  // This would wrap with actual store providers in a real implementation
  return children;
};

// Custom render function that includes providers
export const renderWithProviders = (
  ui,
  {
    initialState = {},
    route = '/',
    ...renderOptions
  } = {}
) => {
  window.history.pushState({}, 'Test page', route);

  const Wrapper = ({ children }) => (
    <BrowserRouter>
      <MockStoreProvider initialState={initialState}>
        {children}
      </MockStoreProvider>
    </BrowserRouter>
  );

  return {
    ...render(ui, { wrapper: Wrapper, ...renderOptions }),
  };
};

// Mock API responses
export const mockApiResponse = (data, status = 200) => {
  return Promise.resolve({
    ok: status >= 200 && status < 300,
    status,
    json: () => Promise.resolve(data),
    text: () => Promise.resolve(JSON.stringify(data)),
  });
};

// Mock API error
export const mockApiError = (message = 'API Error', status = 500) => {
  return Promise.reject({
    response: {
      status,
      data: { detail: message },
    },
    message,
  });
};

// Mock file for testing file uploads
export const createMockFile = (
  name = 'test.jpg',
  size = 1024,
  type = 'image/jpeg'
) => {
  const file = new File(['test content'], name, { type });
  Object.defineProperty(file, 'size', { value: size });
  return file;
};

// Mock image load event
export const mockImageLoad = (img) => {
  Object.defineProperty(img, 'naturalWidth', { value: 800 });
  Object.defineProperty(img, 'naturalHeight', { value: 600 });
  img.onload();
};

// Mock image error event
export const mockImageError = (img) => {
  img.onerror();
};

// Wait for async operations
export const waitFor = (callback, timeout = 1000) => {
  return new Promise((resolve, reject) => {
    const startTime = Date.now();
    
    const check = () => {
      try {
        const result = callback();
        if (result) {
          resolve(result);
        } else if (Date.now() - startTime > timeout) {
          reject(new Error('Timeout waiting for condition'));
        } else {
          setTimeout(check, 10);
        }
      } catch (error) {
        if (Date.now() - startTime > timeout) {
          reject(error);
        } else {
          setTimeout(check, 10);
        }
      }
    };
    
    check();
  });
};

// Mock intersection observer entry
export const createMockIntersectionObserverEntry = (isIntersecting = true) => ({
  isIntersecting,
  intersectionRatio: isIntersecting ? 1 : 0,
  target: document.createElement('div'),
  boundingClientRect: {
    top: 0,
    left: 0,
    bottom: 100,
    right: 100,
    width: 100,
    height: 100,
  },
  rootBounds: {
    top: 0,
    left: 0,
    bottom: 1000,
    right: 1000,
    width: 1000,
    height: 1000,
  },
  intersectionRect: {
    top: 0,
    left: 0,
    bottom: 100,
    right: 100,
    width: 100,
    height: 100,
  },
  time: Date.now(),
});

// Test data factories
export const createMockUser = (overrides = {}) => ({
  id: 1,
  username: 'testuser',
  email: 'test@example.com',
  first_name: 'Test',
  last_name: 'User',
  ...overrides,
});

export const createMockVisualizationRequest = (overrides = {}) => ({
  id: 1,
  user: createMockUser(),
  original_image_url: 'http://example.com/image.jpg',
  screen_type_name: 'Security',
  status: 'pending',
  created_at: '2023-01-01T00:00:00Z',
  result_count: 0,
  ...overrides,
});

export const createMockScreenType = (overrides = {}) => ({
  id: 1,
  name: 'Security',
  description: 'Security screen type',
  is_active: true,
  ...overrides,
});

// Re-export everything from testing library
export * from '@testing-library/react';
export { default as userEvent } from '@testing-library/user-event';
