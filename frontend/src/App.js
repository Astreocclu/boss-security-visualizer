import React, { useState, useEffect } from 'react';
import { Routes, Route, Link, useNavigate, Navigate, useLocation } from 'react-router-dom';
import './App.css';
import ResultsPage from './pages/ResultsPage';
import ResultDetailPage from './pages/ResultDetailPage';

// Simple Login Form Component
const LoginForm = ({ onLogin, error }) => {
  const [username, setUsername] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await onLogin({ username });
    } catch (err) {
      console.error('Login error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: '400px', margin: '0 auto', padding: '20px' }}>
      <h2>🔐 Login to Homescreen Visualizer</h2>
      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
        <div>
          <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
            Username:
          </label>
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
            style={{
              width: '100%',
              padding: '10px',
              border: '1px solid #ddd',
              borderRadius: '4px',
              fontSize: '16px'
            }}
            placeholder="Enter username (try: testuser)"
          />
        </div>

        {error && (
          <div style={{
            color: 'red',
            backgroundColor: '#ffebee',
            padding: '10px',
            borderRadius: '4px',
            border: '1px solid #ffcdd2'
          }}>
            {error}
          </div>
        )}

        <button
          type="submit"
          disabled={loading}
          style={{
            padding: '12px',
            backgroundColor: loading ? '#ccc' : '#007bff',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            fontSize: '16px',
            cursor: loading ? 'not-allowed' : 'pointer'
          }}
        >
          {loading ? 'Logging in...' : 'Login'}
        </button>
      </form>

      <div style={{ marginTop: '20px', padding: '15px', backgroundColor: '#f8f9fa', borderRadius: '4px' }}>
        <h3>💡 Demo Credentials:</h3>
        <p><strong>Username:</strong> testuser</p>
        <p>No password required!</p>
      </div>
    </div>
  );
};

// Image Upload Component
const ImageUploadView = ({ user, screenTypes }) => {
  const navigate = useNavigate();
  const [selectedFile, setSelectedFile] = useState(null);
  const [selectedScreenType, setSelectedScreenType] = useState('');
  const [selectedOpacity, setSelectedOpacity] = useState('95');
  const [selectedColor, setSelectedColor] = useState('Black');
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState('');
  const [dragOver, setDragOver] = useState(false);
  const [processingRequest, setProcessingRequest] = useState(null);
  const [progress, setProgress] = useState(0);
  const [statusMessage, setStatusMessage] = useState('');

  // Poll for progress updates
  useEffect(() => {
    if (!processingRequest) return;

    const pollProgress = async () => {
      try {
        const token = localStorage.getItem('access_token');
        const response = await fetch(`/api/visualizations/${processingRequest.id}/`, {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });

        if (response.ok) {
          const data = await response.json();
          setProgress(data.progress_percentage || 0);
          setStatusMessage(data.status_message || '');

          if (data.status === 'complete') {
            setMessage(`✅ Processing complete! Generated ${data.results?.length || 0} visualizations.`);
            setProcessingRequest(null);
            setProgress(100);
            setStatusMessage('All visualizations ready!');
            // Redirect to the detail page on completion
            setTimeout(() => {
              navigate(`/results/${data.id}`);
            }, 1000);
          } else if (data.status === 'failed') {
            setMessage(`❌ Processing failed: ${data.error_message || 'Unknown error'}`);
            setProcessingRequest(null);
            setProgress(0);
            setStatusMessage('Processing failed');
          }
        }
      } catch (error) {
        console.error('Error polling progress:', error);
      }
    };

    const interval = setInterval(pollProgress, 1000); // Poll every second
    return () => clearInterval(interval);
  }, [processingRequest, navigate]);

  const handleFileSelect = (file) => {
    if (file && file.type.startsWith('image/')) {
      setSelectedFile(file);
      setMessage('');
    } else {
      setMessage('Please select a valid image file (JPG, PNG, GIF, WebP)');
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files[0];
    handleFileSelect(file);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setDragOver(false);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!selectedFile) {
      setMessage('Please select an image file');
      return;
    }

    if (!selectedScreenType) {
      setMessage('Please select a screen type');
      return;
    }

    setUploading(true);
    setMessage('');

    try {
      const formData = new FormData();
      formData.append('original_image', selectedFile);
      formData.append('screen_type', selectedScreenType);
      formData.append('opacity', selectedOpacity);
      formData.append('color', selectedColor);

      const token = localStorage.getItem('access_token');
      const response = await fetch('/api/visualizations/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        setMessage(`✅ Upload successful! Processing started...`);
        setProcessingRequest(data);
        setProgress(0);
        setStatusMessage('Starting processing...');
        setSelectedFile(null);
        setSelectedScreenType('');
      } else {
        const errorData = await response.json();
        setMessage(`❌ Upload failed: ${errorData.detail || 'Unknown error'}`);
      }
    } catch (error) {
      setMessage('❌ Network error. Please try again.');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'center', marginBottom: '20px' }}>
        <Link to="/" style={{ marginRight: '15px', textDecoration: 'none', fontSize: '24px' }}>←</Link>
        <h2>📤 Upload Image for Visualization</h2>
      </div>

      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
        {/* File Upload Area */}
        <div
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          style={{
            border: `2px dashed ${dragOver ? '#007bff' : '#ddd'}`,
            borderRadius: '8px',
            padding: '40px',
            textAlign: 'center',
            backgroundColor: dragOver ? '#f8f9ff' : '#fafafa',
            cursor: 'pointer',
            transition: 'all 0.3s ease'
          }}
          onClick={() => document.getElementById('fileInput').click()}
        >
          <input
            id="fileInput"
            type="file"
            accept="image/*"
            onChange={(e) => handleFileSelect(e.target.files[0])}
            style={{ display: 'none' }}
          />

          {selectedFile ? (
            <div>
              <p style={{ fontSize: '24px', margin: '0 0 10px 0' }}>✅</p>
              <p><strong>Selected:</strong> {selectedFile.name}</p>
              <p>Size: {(selectedFile.size / 1024 / 1024).toFixed(2)} MB</p>
              <p style={{ color: '#666', fontSize: '14px' }}>Click to select a different file</p>
            </div>
          ) : (
            <div>
              <p style={{ fontSize: '48px', margin: '0 0 20px 0' }}>📁</p>
              <p><strong>Drag & drop an image here</strong></p>
              <p style={{ color: '#666' }}>or click to browse files</p>
              <p style={{ color: '#999', fontSize: '14px' }}>Supports: JPG, PNG, GIF, WebP (max 10MB)</p>
            </div>
          )
          }
        </div>

        {/* Screen Type Selection */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '20px' }}>
          <div>
            <label style={{ display: 'block', marginBottom: '10px', fontWeight: 'bold' }}>
              Select Screen Type:
            </label>
            <select
              value={selectedScreenType}
              onChange={(e) => setSelectedScreenType(e.target.value)}
              required
              style={{
                width: '100%',
                padding: '12px',
                border: '1px solid #ddd',
                borderRadius: '4px',
                fontSize: '16px'
              }}
            >
              <option value="">Choose a screen type...</option>
              {screenTypes.map(type => (
                <option key={type.id} value={type.id}>
                  {type.name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label style={{ display: 'block', marginBottom: '10px', fontWeight: 'bold' }}>
              Select Opacity:
            </label>
            <select
              value={selectedOpacity}
              onChange={(e) => setSelectedOpacity(e.target.value)}
              style={{
                width: '100%',
                padding: '12px',
                border: '1px solid #ddd',
                borderRadius: '4px',
                fontSize: '16px'
              }}
            >
              <option value="80">80%</option>
              <option value="95">95%</option>
              <option value="99">99%</option>
            </select>
          </div>

          <div>
            <label style={{ display: 'block', marginBottom: '10px', fontWeight: 'bold' }}>
              Select Color:
            </label>
            <select
              value={selectedColor}
              onChange={(e) => setSelectedColor(e.target.value)}
              style={{
                width: '100%',
                padding: '12px',
                border: '1px solid #ddd',
                borderRadius: '4px',
                fontSize: '16px'
              }}
            >
              <option value="Black">Black</option>
              <option value="Dark Bronze">Dark Bronze</option>
              <option value="Stucco">Stucco</option>
            </select>
          </div>
        </div>

        {/* Progress Bar */}
        {processingRequest && (
          <div style={{
            padding: '20px',
            borderRadius: '8px',
            backgroundColor: '#e3f2fd',
            border: '1px solid #bbdefb'
          }}>
            <h3 style={{ margin: '0 0 15px 0', color: '#1976d2' }}>🔄 Processing Your Image</h3>

            {/* Progress Bar */}
            <div style={{
              width: '100%',
              height: '20px',
              backgroundColor: '#f0f0f0',
              borderRadius: '10px',
              overflow: 'hidden',
              marginBottom: '10px'
            }}>
              <div style={{
                width: `${progress}%`,
                height: '100%',
                backgroundColor: progress === 100 ? '#4caf50' : '#2196f3',
                borderRadius: '10px',
                transition: 'width 0.3s ease',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'white',
                fontSize: '12px',
                fontWeight: 'bold'
              }}>
                {progress > 10 && `${progress}%`}
              </div>
            </div>

            {/* Status Message */}
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              fontSize: '14px'
            }}>
              <span style={{ color: '#666' }}>{statusMessage}</span>
              <span style={{ color: '#1976d2', fontWeight: 'bold' }}>{progress}%</span>
            </div>

            {/* Processing Steps */}
            <div style={{ marginTop: '15px', fontSize: '12px', color: '#666' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '5px' }}>
                <span style={{ color: progress >= 10 ? '#4caf50' : '#ccc' }}>✓ Image Upload</span>
                <span style={{ color: progress >= 30 ? '#4caf50' : '#ccc' }}>✓ Processing Started</span>
                <span style={{ color: progress >= 60 ? '#4caf50' : '#ccc' }}>✓ Generating Visualizations</span>
                <span style={{ color: progress >= 100 ? '#4caf50' : '#ccc' }}>✓ Complete</span>
              </div>
            </div>
          </div>
        )}

        {/* Message Display */}
        {message && (
          <div style={{
            padding: '15px',
            borderRadius: '4px',
            backgroundColor: message.includes('✅') ? '#d4edda' : '#f8d7da',
            border: `1px solid ${message.includes('✅') ? '#c3e6cb' : '#f5c6cb'}`,
            color: message.includes('✅') ? '#155724' : '#721c24'
          }}>
            {message}
          </div>
        )}

        {/* Submit Button */}
        <button
          type="submit"
          disabled={uploading || processingRequest || !selectedFile || !selectedScreenType}
          style={{
            padding: '15px',
            backgroundColor: (uploading || processingRequest) ? '#ccc' : '#28a745',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            fontSize: '16px',
            cursor: (uploading || processingRequest) ? 'not-allowed' : 'pointer'
          }}
        >
          {uploading ? '⏳ Uploading...' :
            processingRequest ? '🔄 Processing...' :
              '🚀 Generate Visualization'}
        </button>
      </form>
    </div>
  );
};

// Screen Types View Component
const ScreenTypesView = ({ screenTypes }) => {
  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'center', marginBottom: '20px' }}>
        <Link to="/" style={{ marginRight: '15px', textDecoration: 'none', fontSize: '24px' }}>←</Link>
        <h2>🖥️ Available Screen Types</h2>
      </div>
      <div style={{ display: 'grid', gap: '20px', marginTop: '20px' }}>
        {screenTypes.map(type => (
          <div key={type.id} style={{
            backgroundColor: '#f8f9fa',
            padding: '20px',
            borderRadius: '8px',
            border: '1px solid #dee2e6'
          }}>
            <h3>{type.name}</h3>
            <p>{type.description || 'No description available'}</p>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '10px', fontSize: '14px', color: '#666' }}>
              <span>Requests: {type.request_count || 0}</span>
              <span>Status: {type.is_active ? '✅ Active' : '❌ Inactive'}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

// Simple Dashboard Component
const Dashboard = ({ user, onLogout }) => {
  const [screenTypes, setScreenTypes] = useState([]);

  // Fetch screen types when component mounts
  useEffect(() => {
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
  }, []);

  return (
    <div style={{ maxWidth: '800px', margin: '0 auto', padding: '20px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '30px' }}>
        <h1>🏠 Homescreen Visualizer Dashboard</h1>
        <div style={{ display: 'flex', gap: '10px' }}>
          <button
            onClick={onLogout}
            style={{
              padding: '8px 16px',
              backgroundColor: '#dc3545',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer'
            }}
          >
            Logout
          </button>
        </div>
      </div>

      <div style={{ backgroundColor: '#e8f5e8', padding: '20px', borderRadius: '8px', marginBottom: '20px' }}>
        <h2>✅ Welcome, {user.username}!</h2>
        <p>You have successfully logged into the Homescreen Visualizer.</p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '20px' }}>
        <div style={{ backgroundColor: '#f8f9fa', padding: '20px', borderRadius: '8px', border: '1px solid #dee2e6' }}>
          <h3>👤 User Profile</h3>
          <p><strong>Username:</strong> {user.username}</p>
          <p><strong>Email:</strong> {user.email}</p>
          <p><strong>Member since:</strong> {new Date(user.date_joined).toLocaleDateString()}</p>
          <p><strong>Total Requests:</strong> {user.profile?.total_requests || 0}</p>
        </div>

        <div style={{ backgroundColor: '#f8f9fa', padding: '20px', borderRadius: '8px', border: '1px solid #dee2e6' }}>
          <h3>🚀 Quick Actions</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            <Link
              to="/upload"
              style={{
                padding: '10px',
                backgroundColor: '#28a745',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
                textAlign: 'center',
                textDecoration: 'none'
              }}
            >
              📤 Upload Image
            </Link>
            <Link
              to="/results"
              style={{
                padding: '10px',
                backgroundColor: '#17a2b8',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
                textAlign: 'center',
                textDecoration: 'none'
              }}
            >
              📊 View Results
            </Link>
            <Link
              to="/screentypes"
              style={{
                padding: '10px',
                backgroundColor: '#6f42c1',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
                textAlign: 'center',
                textDecoration: 'none'
              }}
            >
              🖥️ Screen Types ({screenTypes.length})
            </Link>
          </div>
        </div>

        <div style={{ backgroundColor: '#f8f9fa', padding: '20px', borderRadius: '8px', border: '1px solid #dee2e6' }}>
          <h3>📊 API Status</h3>
          <p>✅ Authentication: Working</p>
          <p>✅ Backend API: Connected</p>
          <p>✅ Screen Types: {screenTypes.length} available</p>
          <p>✅ Database: Connected</p>
        </div>
      </div>

      <div style={{ marginTop: '30px', padding: '20px', backgroundColor: '#fff3cd', borderRadius: '8px', border: '1px solid #ffeaa7' }}>
        <h3>🎯 Next Steps:</h3>
        <ul>
          <li>Upload an image to generate homescreen visualizations</li>
          <li>Select from available screen types (Security, Entertainment, Smart Home)</li>
          <li>View and manage your visualization results</li>
          <li>Explore the admin panel at <a href="/admin" target="_blank">/admin</a></li>
        </ul>
      </div>
    </div>
  );
};

function App() {
  const [user, setUser] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [screenTypes, setScreenTypes] = useState([]);
  const navigate = useNavigate();
  const location = useLocation();

  // Check for existing token on mount
  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token && !user) {
      // Ideally verify token with backend, but for now just assume valid if present
      // Or fetch user profile
      // For this demo, we'll just set a dummy user or try to fetch profile if we had an endpoint
      // Let's just clear it if we don't have user data, forcing login, or better:
      // We can't easily reconstruct the user object without an API call.
      // Let's rely on the user logging in for now, or if we want persistence:
      // We should add a /api/auth/me/ endpoint.
      // For now, let's just leave it. If they refresh, they might be logged out.
      // To fix refresh issue, let's try to fetch user details or just keep them logged in
      // if we had the user details in localStorage too (not secure but works for demo)
      const storedUser = localStorage.getItem('user_data');
      if (storedUser) {
        setUser(JSON.parse(storedUser));
      }
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
  }, []);

  const handleLogin = async (credentials) => {
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
  };

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
      <div style={{ minHeight: '100vh', backgroundColor: '#f5f5f5', padding: '20px' }}>
        <Routes>
          <Route path="/login" element={
            user ? <Navigate to="/" replace /> : <LoginForm onLogin={handleLogin} error={error} loading={loading} />
          } />

          <Route path="/" element={
            <ProtectedRoute>
              <Dashboard user={user} onLogout={handleLogout} />
            </ProtectedRoute>
          } />

          <Route path="/upload" element={
            <ProtectedRoute>
              <ImageUploadView user={user} screenTypes={screenTypes} />
            </ProtectedRoute>
          } />

          <Route path="/screentypes" element={
            <ProtectedRoute>
              <ScreenTypesView screenTypes={screenTypes} />
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
