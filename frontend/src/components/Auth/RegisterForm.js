import React, { useState } from 'react';
import PropTypes from 'prop-types';
import { FormInput, Button, ErrorMessage } from '../Common';
import './RegisterForm.css';

const RegisterForm = ({ onRegister, error, loading: externalLoading = false }) => {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: ''
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

    // Username validation
    if (!formData.username.trim()) {
      errors.username = 'Username is required';
    } else if (formData.username.length < 3) {
      errors.username = 'Username must be at least 3 characters';
    }

    // Email validation
    if (!formData.email.trim()) {
      errors.email = 'Email is required';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      errors.email = 'Please enter a valid email address';
    }

    // Password validation
    if (!formData.password) {
      errors.password = 'Password is required';
    } else if (formData.password.length < 6) {
      errors.password = 'Password must be at least 6 characters';
    }

    // Confirm password validation
    if (!formData.confirmPassword) {
      errors.confirmPassword = 'Please confirm your password';
    } else if (formData.password !== formData.confirmPassword) {
      errors.confirmPassword = 'Passwords do not match';
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
      const { confirmPassword, ...registrationData } = formData;
      await onRegister(registrationData);
      // Form will be reset by navigation after successful registration
    } catch (error) {
      console.error('Registration error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="register-form">
      <form onSubmit={handleSubmit} noValidate>
        <FormInput
          label="Username"
          name="username"
          type="text"
          value={formData.username}
          onChange={handleInputChange}
          error={validationErrors.username}
          helperText="At least 3 characters"
          required
          disabled={loading}
          fullWidth
          autoComplete="username"
        />

        <FormInput
          label="Email"
          name="email"
          type="email"
          value={formData.email}
          onChange={handleInputChange}
          error={validationErrors.email}
          required
          disabled={loading}
          fullWidth
          autoComplete="email"
        />

        <FormInput
          label="Password"
          name="password"
          type="password"
          value={formData.password}
          onChange={handleInputChange}
          error={validationErrors.password}
          helperText="At least 6 characters"
          required
          disabled={loading}
          fullWidth
          autoComplete="new-password"
        />

        <FormInput
          label="Confirm Password"
          name="confirmPassword"
          type="password"
          value={formData.confirmPassword}
          onChange={handleInputChange}
          error={validationErrors.confirmPassword}
          required
          disabled={loading}
          fullWidth
          autoComplete="new-password"
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
          Register
        </Button>
      </form>
    </div>
  );
};

RegisterForm.propTypes = {
  onRegister: PropTypes.func.isRequired,
  error: PropTypes.string,
  loading: PropTypes.bool
};

export default React.memo(RegisterForm);
