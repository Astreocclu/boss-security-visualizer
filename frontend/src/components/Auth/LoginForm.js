import React, { useState } from 'react';
import PropTypes from 'prop-types';
import { FormInput, Button, ErrorMessage } from '../Common';
import './LoginForm.css';

const LoginForm = ({ onLogin, error, loading: externalLoading = false }) => {
  const [formData, setFormData] = useState({
    username: ''
  });
  const [validationErrors, setValidationErrors] = useState({});
  const [isLoading, setIsLoading] = useState(false);

  const loading = isLoading || externalLoading;

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));

    // Clear validation error when user starts typing
    if (validationErrors[name]) {
      setValidationErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  const validateForm = () => {
    const errors = {};

    if (!formData.username.trim()) {
      errors.username = 'Username is required';
    }

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setIsLoading(true);

    try {
      await onLogin(formData);
      // Form will be reset by navigation after successful login
    } catch (error) {
      console.error('Login error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="login-form">
      <form onSubmit={handleSubmit} noValidate>
        <FormInput
          label="Username"
          name="username"
          type="text"
          value={formData.username}
          onChange={handleInputChange}
          error={validationErrors.username}
          required
          disabled={loading}
          fullWidth
          autoComplete="username"
        />

        <ErrorMessage message={error} type="error" />

        <Button
          type="submit"
          variant="primary"
          size="large"
          fullWidth
          loading={loading}
          disabled={loading}
        >
          Login
        </Button>
      </form>
    </div>
  );
};

LoginForm.propTypes = {
  onLogin: PropTypes.func.isRequired,
  error: PropTypes.string,
  loading: PropTypes.bool
};

export default React.memo(LoginForm);
