# Frontend Component Documentation

## Overview

This document provides comprehensive documentation for all React components in the Homescreen Visualizer application.

## Component Architecture

The application follows a modular component architecture with the following structure:

```
src/components/
├── Common/           # Reusable UI components
├── Layout/           # Layout and navigation components
├── Grid/             # Grid system components
├── ErrorBoundary/    # Error handling components
├── LazyLoad/         # Performance optimization components
├── OptimizedImage/   # Image optimization components
├── VirtualList/      # Virtual scrolling components
├── Upload/           # File upload components
└── Navigation/       # Navigation components
```

## Common Components

### Button

A versatile button component with multiple variants and states.

**Props:**
```typescript
interface ButtonProps {
  children: React.ReactNode;
  variant?: 'primary' | 'secondary' | 'outline' | 'danger';
  size?: 'small' | 'medium' | 'large';
  loading?: boolean;
  disabled?: boolean;
  fullWidth?: boolean;
  type?: 'button' | 'submit' | 'reset';
  onClick?: (event: React.MouseEvent<HTMLButtonElement>) => void;
  className?: string;
}
```

**Usage:**
```jsx
import { Button } from '../components/Common';

// Basic usage
<Button onClick={handleClick}>Click me</Button>

// With variants
<Button variant="primary">Primary</Button>
<Button variant="secondary">Secondary</Button>
<Button variant="outline">Outline</Button>
<Button variant="danger">Danger</Button>

// With sizes
<Button size="small">Small</Button>
<Button size="medium">Medium</Button>
<Button size="large">Large</Button>

// With states
<Button loading>Loading...</Button>
<Button disabled>Disabled</Button>
<Button fullWidth>Full Width</Button>
```

### FormInput

A comprehensive form input component with validation and error handling.

**Props:**
```typescript
interface FormInputProps {
  label?: string;
  type?: string;
  value?: string;
  onChange?: (event: React.ChangeEvent<HTMLInputElement>) => void;
  error?: string;
  helperText?: string;
  required?: boolean;
  disabled?: boolean;
  fullWidth?: boolean;
  placeholder?: string;
  id?: string;
  className?: string;
}
```

**Usage:**
```jsx
import { FormInput } from '../components/Common';

<FormInput
  label="Email"
  type="email"
  value={email}
  onChange={(e) => setEmail(e.target.value)}
  error={emailError}
  helperText="Enter your email address"
  required
  fullWidth
/>
```

### LoadingSpinner

A customizable loading spinner component.

**Props:**
```typescript
interface LoadingSpinnerProps {
  size?: 'small' | 'medium' | 'large';
  text?: string;
  className?: string;
}
```

**Usage:**
```jsx
import { LoadingSpinner } from '../components/Common';

<LoadingSpinner size="large" text="Loading..." />
```

### ErrorMessage

A component for displaying error messages with consistent styling.

**Props:**
```typescript
interface ErrorMessageProps {
  message: string;
  type?: 'error' | 'warning' | 'info';
  dismissible?: boolean;
  onDismiss?: () => void;
  className?: string;
}
```

**Usage:**
```jsx
import { ErrorMessage } from '../components/Common';

<ErrorMessage
  message="Something went wrong"
  type="error"
  dismissible
  onDismiss={handleDismiss}
/>
```

## Layout Components

### Layout

A flexible layout component that provides structure for pages.

**Props:**
```typescript
interface LayoutProps {
  children: React.ReactNode;
  sidebar?: React.ReactNode;
  header?: React.ReactNode;
  footer?: React.ReactNode;
  className?: string;
  fluid?: boolean;
}
```

**Usage:**
```jsx
import { Layout } from '../components/Layout';

<Layout
  header={<Navigation />}
  sidebar={<Sidebar />}
  footer={<Footer />}
>
  <MainContent />
</Layout>
```

### Navigation

A responsive navigation component with user menu and mobile support.

**Props:**
```typescript
interface NavigationProps {
  title?: string;
  showUserMenu?: boolean;
  className?: string;
}
```

**Usage:**
```jsx
import { Navigation } from '../components/Navigation';

<Navigation
  title="Homescreen Visualizer"
  showUserMenu={true}
/>
```

## Grid System

### Container, Row, Col

A flexible grid system based on CSS Flexbox.

**Container Props:**
```typescript
interface ContainerProps {
  children: React.ReactNode;
  fluid?: boolean;
  className?: string;
}
```

**Row Props:**
```typescript
interface RowProps {
  children: React.ReactNode;
  gutter?: 'none' | 'small' | 'medium' | 'large';
  align?: 'start' | 'center' | 'end' | 'stretch';
  justify?: 'start' | 'center' | 'end' | 'between' | 'around' | 'evenly';
  className?: string;
}
```

**Col Props:**
```typescript
interface ColProps {
  children: React.ReactNode;
  xs?: number | string;
  sm?: number | string;
  md?: number | string;
  lg?: number | string;
  xl?: number | string;
  offset?: number | string;
  className?: string;
}
```

**Usage:**
```jsx
import { Container, Row, Col } from '../components/Grid';

<Container>
  <Row gutter="medium">
    <Col md={6} lg={4}>
      <Card>Content 1</Card>
    </Col>
    <Col md={6} lg={8}>
      <Card>Content 2</Card>
    </Col>
  </Row>
</Container>
```

## Performance Components

### LazyLoad

A component for lazy loading content with intersection observer.

**Props:**
```typescript
interface LazyLoadProps {
  children: React.ReactNode;
  fallback?: React.ReactNode;
  errorFallback?: (error: Error, errorInfo: ErrorInfo, retry: () => void) => React.ReactNode;
  className?: string;
  minHeight?: string;
}
```

**Usage:**
```jsx
import { LazyLoad } from '../components/LazyLoad';

<LazyLoad fallback={<LoadingSpinner />}>
  <ExpensiveComponent />
</LazyLoad>
```

### OptimizedImage

An optimized image component with lazy loading and responsive images.

**Props:**
```typescript
interface OptimizedImageProps {
  src: string;
  alt: string;
  width?: number | string;
  height?: number | string;
  className?: string;
  placeholder?: React.ReactNode;
  lazy?: boolean;
  quality?: 'auto' | 'low' | 'medium' | 'high';
  sizes?: string;
  srcSet?: string;
  onLoad?: (event: React.SyntheticEvent<HTMLImageElement>) => void;
  onError?: (event: React.SyntheticEvent<HTMLImageElement>) => void;
}
```

**Usage:**
```jsx
import { OptimizedImage } from '../components/OptimizedImage';

<OptimizedImage
  src="/images/example.jpg"
  alt="Example image"
  width={400}
  height={300}
  lazy={true}
  quality="high"
/>
```

### VirtualList

A virtual scrolling component for large lists.

**Props:**
```typescript
interface VirtualListProps {
  items: any[];
  itemHeight?: number;
  containerHeight?: number | string;
  renderItem: (item: any, index: number) => React.ReactNode;
  overscan?: number;
  className?: string;
  onScroll?: (event: React.UIEvent, scrollTop: number) => void;
}
```

**Usage:**
```jsx
import { VirtualList } from '../components/VirtualList';

<VirtualList
  items={largeDataSet}
  itemHeight={50}
  containerHeight={400}
  renderItem={(item, index) => (
    <div key={item.id}>
      {item.name}
    </div>
  )}
/>
```

## Error Handling

### ErrorBoundary

A React error boundary component for graceful error handling.

**Props:**
```typescript
interface ErrorBoundaryProps {
  children: React.ReactNode;
  fallback?: (error: Error, errorInfo: ErrorInfo, retry: () => void) => React.ReactNode;
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
  title?: string;
  message?: string;
}
```

**Usage:**
```jsx
import { ErrorBoundary } from '../components/ErrorBoundary';

<ErrorBoundary
  title="Something went wrong"
  message="Please try refreshing the page"
  onError={(error, errorInfo) => {
    console.error('Error caught by boundary:', error, errorInfo);
  }}
>
  <App />
</ErrorBoundary>
```

## Upload Components

### ImageUploader

A comprehensive image upload component with drag-and-drop support.

**Props:**
```typescript
interface ImageUploaderProps {
  onImageSelect: (file: File | null) => void;
  acceptedTypes?: string[];
  maxSize?: number;
  disabled?: boolean;
  className?: string;
}
```

**Usage:**
```jsx
import { ImageUploader } from '../components/Upload';

<ImageUploader
  onImageSelect={handleImageSelect}
  acceptedTypes={['image/jpeg', 'image/png']}
  maxSize={10 * 1024 * 1024} // 10MB
  disabled={uploading}
/>
```

## Styling Guidelines

### CSS Classes

All components use BEM (Block Element Modifier) naming convention:

```css
.component-name { }
.component-name__element { }
.component-name--modifier { }
```

### Responsive Design

Components use mobile-first responsive design with these breakpoints:

- **xs**: 0px and up
- **sm**: 576px and up
- **md**: 768px and up
- **lg**: 992px and up
- **xl**: 1200px and up

### Accessibility

All components follow WCAG 2.1 AA guidelines:

- Proper ARIA labels and roles
- Keyboard navigation support
- Focus management
- Color contrast compliance
- Screen reader compatibility

## Testing

### Component Testing

Each component includes comprehensive tests:

```javascript
import { render, screen, fireEvent } from '@testing-library/react';
import { Button } from '../Button';

test('renders button with text', () => {
  render(<Button>Click me</Button>);
  expect(screen.getByRole('button')).toHaveTextContent('Click me');
});

test('calls onClick when clicked', () => {
  const handleClick = jest.fn();
  render(<Button onClick={handleClick}>Click me</Button>);
  fireEvent.click(screen.getByRole('button'));
  expect(handleClick).toHaveBeenCalledTimes(1);
});
```

### Testing Utilities

Use the provided test utilities for consistent testing:

```javascript
import { renderWithProviders, createMockUser } from '../../utils/testUtils';

test('component with providers', () => {
  const user = createMockUser();
  renderWithProviders(<Component />, {
    initialState: { user }
  });
});
```

## Performance Considerations

### Memoization

Components are memoized using `React.memo` where appropriate:

```javascript
export default React.memo(Component);
```

### Code Splitting

Use dynamic imports for code splitting:

```javascript
const LazyComponent = React.lazy(() => import('./LazyComponent'));
```

### Bundle Optimization

- Tree shaking enabled for unused code elimination
- Dynamic imports for route-based code splitting
- Image optimization with WebP support
- CSS optimization with purging unused styles
