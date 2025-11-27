import React, { Suspense } from 'react';
import PropTypes from 'prop-types';
import { LoadingSpinner, ErrorBoundary } from '../Common';
import './LazyLoad.css';

const LazyLoad = ({ 
  children, 
  fallback = null,
  errorFallback = null,
  className = '',
  minHeight = '200px'
}) => {
  const defaultFallback = (
    <div className="lazy-load-fallback" style={{ minHeight }}>
      <LoadingSpinner size="large" text="Loading..." />
    </div>
  );

  const defaultErrorFallback = (error, errorInfo, retry) => (
    <div className="lazy-load-error">
      <ErrorBoundary
        title="Failed to load component"
        message="This component failed to load. Please try again."
        fallback={() => (
          <div className="lazy-load-error-content">
            <p>Component failed to load</p>
            <button onClick={retry} className="lazy-load-retry-btn">
              Retry
            </button>
          </div>
        )}
      />
    </div>
  );

  const lazyLoadClasses = [
    'lazy-load',
    className
  ].filter(Boolean).join(' ');

  return (
    <div className={lazyLoadClasses}>
      <ErrorBoundary fallback={errorFallback || defaultErrorFallback}>
        <Suspense fallback={fallback || defaultFallback}>
          {children}
        </Suspense>
      </ErrorBoundary>
    </div>
  );
};

LazyLoad.propTypes = {
  children: PropTypes.node.isRequired,
  fallback: PropTypes.node,
  errorFallback: PropTypes.func,
  className: PropTypes.string,
  minHeight: PropTypes.string
};

// Higher-order component for lazy loading
export const withLazyLoad = (importFunc, options = {}) => {
  const LazyComponent = React.lazy(importFunc);
  
  return (props) => (
    <LazyLoad {...options}>
      <LazyComponent {...props} />
    </LazyLoad>
  );
};

// Hook for lazy loading with intersection observer
export const useLazyLoad = (ref, options = {}) => {
  const [isVisible, setIsVisible] = React.useState(false);
  const [hasLoaded, setHasLoaded] = React.useState(false);

  React.useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting && !hasLoaded) {
          setIsVisible(true);
          setHasLoaded(true);
        }
      },
      {
        threshold: 0.1,
        rootMargin: '50px',
        ...options
      }
    );

    if (ref.current) {
      observer.observe(ref.current);
    }

    return () => {
      if (ref.current) {
        observer.unobserve(ref.current);
      }
    };
  }, [ref, hasLoaded, options]);

  return { isVisible, hasLoaded };
};

export default LazyLoad;
