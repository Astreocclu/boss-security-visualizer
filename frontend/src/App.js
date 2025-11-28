import React, { useState, useEffect, useCallback } from 'react';
import { Routes, Route, useNavigate, Navigate, useLocation } from 'react-router-dom';
import './App.css';
import ResultsPage from './pages/ResultsPage';
import ResultDetailPage from './pages/ResultDetailPage';
import UploadPage from './pages/UploadPage';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import ScreenTypesPage from './pages/ScreenTypesPage';

function App() {
  const [user, setUser] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [screenTypes, setScreenTypes] = useState([]);
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogin = useCallback(async (credentials) => {
    setLoading(true);
    setError('');

    try {
      const response = await fetch('/api/auth/login/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(credentials),
      });

      if (response.ok) {
        const data = await response.json();
        setUser(data.user);
        // Store tokens in localStorage
        localStorage.setItem('access_token', data.access);
        localStorage.setItem('refresh_token', data.refresh);
        localStorage.setItem('user_data', JSON.stringify(data.user));
        navigate('/');
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Login failed');
      }
    } catch (err) {
      setError('Network error. Please check your connection.');
    } finally {
      setLoading(false);
    }
  }, [navigate]);

  // Check for existing token on mount
  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token && !user) {
      const storedUser = localStorage.getItem('user_data');
      if (storedUser) {
        setUser(JSON.parse(storedUser));
      }
    } else if (!token && !user) {
      // Auto-login as Guest if no session exists
      handleLogin({ username: 'Guest' });
    }

    // Fetch screen types for global use
    const fetchScreenTypes = async () => {
      try {
        const response = await fetch('/api/screentypes/');
        if (response.ok) {
          const data = await response.json();
          setScreenTypes(data.results || []);
        }
      } catch (error) {
        console.error('Error fetching screen types:', error);
      }
    };
    fetchScreenTypes();
  }, [handleLogin, user]);

  const handleLogout = () => {
    setUser(null);
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user_data');
    navigate('/login');
  };

  // Protected Route Wrapper
  const ProtectedRoute = ({ children }) => {
    if (!user) {
      return <Navigate to="/login" state={{ from: location }} replace />;
    }
    return children;
  };

  return (
    <div className="App">
      <div style={{ minHeight: '100vh', backgroundColor: 'var(--primary-navy)', padding: '20px' }}>
        <Routes>
          <Route path="/login" element={
            user ? <Navigate to="/" replace /> : <LoginPage onLogin={handleLogin} error={error} loading={loading} />
          } />

          <Route path="/" element={
            <ProtectedRoute>
              <DashboardPage user={user} onLogout={handleLogout} />
            </ProtectedRoute>
          } />

          <Route path="/upload" element={
            <ProtectedRoute>
              <UploadPage />
            </ProtectedRoute>
          } />

          <Route path="/screentypes" element={
            <ProtectedRoute>
              <ScreenTypesPage screenTypes={screenTypes} />
            </ProtectedRoute>
          } />

          <Route path="/results" element={
            <ProtectedRoute>
              <ResultsPage />
            </ProtectedRoute>
          } />

          <Route path="/results/:id" element={
            <ProtectedRoute>
              <ResultDetailPage />
            </ProtectedRoute>
          } />
        </Routes>
      </div>
    </div>
  );
}

export default App;
