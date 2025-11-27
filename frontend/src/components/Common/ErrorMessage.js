import React from 'react';
import PropTypes from 'prop-types';
import './ErrorMessage.css';

const ErrorMessage = ({ 
  message, 
  type = 'error', 
  dismissible = false, 
  onDismiss,
  className = '',
  icon = true 
}) => {
  if (!message) return null;

  const typeClasses = {
    error: 'error-message-error',
    warning: 'error-message-warning',
    info: 'error-message-info',
    success: 'error-message-success'
  };

  const icons = {
    error: '❌',
    warning: '⚠️',
    info: 'ℹ️',
    success: '✅'
  };

  const messageClasses = [
    'error-message',
    typeClasses[type],
    className
  ].filter(Boolean).join(' ');

  return (
    <div className={messageClasses} role="alert">
      {icon && <span className="error-message-icon">{icons[type]}</span>}
      <span className="error-message-text">{message}</span>
      {dismissible && (
        <button 
          className="error-message-dismiss"
          onClick={onDismiss}
          aria-label="Dismiss message"
        >
          ×
        </button>
      )}
    </div>
  );
};

ErrorMessage.propTypes = {
  message: PropTypes.string,
  type: PropTypes.oneOf(['error', 'warning', 'info', 'success']),
  dismissible: PropTypes.bool,
  onDismiss: PropTypes.func,
  className: PropTypes.string,
  icon: PropTypes.bool
};

export default React.memo(ErrorMessage);
