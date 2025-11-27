import React, { forwardRef } from 'react';
import PropTypes from 'prop-types';
import './FormInput.css';

const FormInput = forwardRef(({
  label,
  error,
  helperText,
  required = false,
  fullWidth = false,
  className = '',
  id,
  ...props
}, ref) => {
  const inputId = id || `input-${Math.random().toString(36).substr(2, 9)}`;
  
  const inputClasses = [
    'form-input',
    error && 'form-input-error',
    fullWidth && 'form-input-full-width',
    className
  ].filter(Boolean).join(' ');

  return (
    <div className="form-input-container">
      {label && (
        <label htmlFor={inputId} className="form-input-label">
          {label}
          {required && <span className="form-input-required">*</span>}
        </label>
      )}
      
      <input
        ref={ref}
        id={inputId}
        className={inputClasses}
        aria-invalid={error ? 'true' : 'false'}
        aria-describedby={
          error ? `${inputId}-error` : 
          helperText ? `${inputId}-helper` : undefined
        }
        {...props}
      />
      
      {error && (
        <div id={`${inputId}-error`} className="form-input-error-text" role="alert">
          {error}
        </div>
      )}
      
      {helperText && !error && (
        <div id={`${inputId}-helper`} className="form-input-helper-text">
          {helperText}
        </div>
      )}
    </div>
  );
});

FormInput.displayName = 'FormInput';

FormInput.propTypes = {
  label: PropTypes.string,
  error: PropTypes.string,
  helperText: PropTypes.string,
  required: PropTypes.bool,
  fullWidth: PropTypes.bool,
  className: PropTypes.string,
  id: PropTypes.string
};

export default React.memo(FormInput);
