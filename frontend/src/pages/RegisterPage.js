import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import RegisterForm from '../components/Auth/RegisterForm';
import { registerUser } from '../services/api';

const RegisterPage = () => {
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleRegister = async (userData) => {
    try {
      await registerUser(userData);
      navigate('/login'); // Redirect to login page after successful registration
    } catch (err) {
      if (err.response?.data) {
        // Format Django REST Framework validation errors
        const errors = err.response.data;
        const errorMessages = [];

        for (const field in errors) {
          if (Array.isArray(errors[field])) {
            errorMessages.push(`${field}: ${errors[field].join(' ')}`);
          }
        }

        setError(errorMessages.join('\n') || 'Registration failed.');
      } else {
        setError('Registration failed. Please try again.');
      }
    }
  };

  return (
    <div className="register-page">
      <h1>Register</h1>
      <RegisterForm onRegister={handleRegister} error={error} />
      <p>
        Already have an account? <Link to="/login">Login</Link>
      </p>
    </div>
  );
};

export default RegisterPage;
