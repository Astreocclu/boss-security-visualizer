import React, { useState, useRef, useEffect } from 'react';
import PropTypes from 'prop-types';
import { LoadingSpinner } from '../Common';
import { useLazyLoad } from '../LazyLoad/LazyLoad';
import './OptimizedImage.css';

const OptimizedImage = ({
  src,
  alt,
  width,
  height,
  className = '',
  placeholder = null,
  lazy = true,
  quality = 'auto',
  sizes = '',
  srcSet = '',
  onLoad,
  onError,
  ...props
}) => {
  const [isLoaded, setIsLoaded] = useState(false);
  const [hasError, setHasError] = useState(false);
  const [imageSrc, setImageSrc] = useState(lazy ? null : src);
  const imgRef = useRef(null);
  const containerRef = useRef(null);
  
  const { isVisible } = useLazyLoad(containerRef, {
    threshold: 0.1,
    rootMargin: '50px'
  });

  useEffect(() => {
    if (lazy && isVisible && !imageSrc) {
      setImageSrc(src);
    } else if (!lazy) {
      setImageSrc(src);
    }
  }, [lazy, isVisible, src, imageSrc]);

  const handleLoad = (e) => {
    setIsLoaded(true);
    setHasError(false);
    onLoad?.(e);
  };

  const handleError = (e) => {
    setHasError(true);
    setIsLoaded(false);
    onError?.(e);
  };

  const generateSrcSet = (baseSrc) => {
    if (srcSet) return srcSet;
    
    // Generate responsive srcSet if not provided
    const formats = ['webp', 'jpg'];
    const sizes = [480, 768, 1024, 1200];
    
    return sizes.map(size => 
      formats.map(format => 
        `${baseSrc}?w=${size}&f=${format} ${size}w`
      ).join(', ')
    ).join(', ');
  };

  const imageClasses = [
    'optimized-image',
    isLoaded && 'optimized-image-loaded',
    hasError && 'optimized-image-error',
    className
  ].filter(Boolean).join(' ');

  const containerClasses = [
    'optimized-image-container',
    !isLoaded && !hasError && 'optimized-image-loading'
  ].filter(Boolean).join(' ');

  const defaultPlaceholder = (
    <div className="optimized-image-placeholder">
      <LoadingSpinner size="medium" />
    </div>
  );

  const errorPlaceholder = (
    <div className="optimized-image-error-placeholder">
      <span className="optimized-image-error-icon">🖼️</span>
      <span className="optimized-image-error-text">Failed to load image</span>
    </div>
  );

  return (
    <div 
      ref={containerRef}
      className={containerClasses}
      style={{ 
        width: width || 'auto', 
        height: height || 'auto',
        aspectRatio: width && height ? `${width}/${height}` : undefined
      }}
    >
      {imageSrc && (
        <img
          ref={imgRef}
          src={imageSrc}
          alt={alt}
          width={width}
          height={height}
          className={imageClasses}
          srcSet={generateSrcSet(imageSrc)}
          sizes={sizes || '(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw'}
          loading={lazy ? 'lazy' : 'eager'}
          decoding="async"
          onLoad={handleLoad}
          onError={handleError}
          {...props}
        />
      )}
      
      {!isLoaded && !hasError && (placeholder || defaultPlaceholder)}
      {hasError && errorPlaceholder}
    </div>
  );
};

OptimizedImage.propTypes = {
  src: PropTypes.string.isRequired,
  alt: PropTypes.string.isRequired,
  width: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
  height: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
  className: PropTypes.string,
  placeholder: PropTypes.node,
  lazy: PropTypes.bool,
  quality: PropTypes.oneOf(['auto', 'low', 'medium', 'high']),
  sizes: PropTypes.string,
  srcSet: PropTypes.string,
  onLoad: PropTypes.func,
  onError: PropTypes.func
};

export default React.memo(OptimizedImage);
