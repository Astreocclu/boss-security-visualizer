import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

const DashboardPage = ({ user, onLogout }) => {
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
        <div className="dashboard-page" style={{ maxWidth: '1200px', margin: '0 auto', padding: '20px' }}>
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

            <div style={{ backgroundColor: 'var(--glass-bg)', padding: '20px', borderRadius: '8px', marginBottom: '20px', border: '1px solid var(--glass-border)' }}>
                <h2>✅ Welcome, {user.username}!</h2>
                <p>You have successfully logged into the Homescreen Visualizer.</p>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '20px' }}>
                <div style={{ backgroundColor: 'var(--glass-bg)', padding: '20px', borderRadius: '8px', border: '1px solid var(--glass-border)' }}>
                    <h3>👤 User Profile</h3>
                    <p><strong>Username:</strong> {user.username}</p>
                    <p><strong>Email:</strong> {user.email}</p>
                    <p><strong>Member since:</strong> {new Date(user.date_joined).toLocaleDateString()}</p>
                    <p><strong>Total Requests:</strong> {user.profile?.total_requests || 0}</p>
                </div>

                <div style={{ backgroundColor: 'var(--glass-bg)', padding: '20px', borderRadius: '8px', border: '1px solid var(--glass-border)' }}>
                    <h3>🚀 Quick Actions</h3>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                        <Link
                            to="/upload"
                            className="btn"
                            style={{
                                textAlign: 'center',
                                textDecoration: 'none',
                                display: 'block'
                            }}
                        >
                            📤 Upload Image
                        </Link>
                        <Link
                            to="/results"
                            className="btn"
                            style={{
                                backgroundColor: '#17a2b8', // Override for different color if needed, or use class
                                textAlign: 'center',
                                textDecoration: 'none',
                                display: 'block'
                            }}
                        >
                            📊 View Results
                        </Link>
                        <Link
                            to="/screentypes"
                            className="btn"
                            style={{
                                backgroundColor: '#6f42c1',
                                textAlign: 'center',
                                textDecoration: 'none',
                                display: 'block'
                            }}
                        >
                            🖥️ Screen Types ({screenTypes.length})
                        </Link>
                    </div>
                </div>

                <div style={{ backgroundColor: 'var(--glass-bg)', padding: '20px', borderRadius: '8px', border: '1px solid var(--glass-border)' }}>
                    <h3>📊 API Status</h3>
                    <p>✅ Authentication: Working</p>
                    <p>✅ Backend API: Connected</p>
                    <p>✅ Screen Types: {screenTypes.length} available</p>
                    <p>✅ Database: Connected</p>
                </div>
            </div>

            <div style={{ marginTop: '30px', padding: '20px', backgroundColor: 'rgba(255, 243, 205, 0.1)', borderRadius: '8px', border: '1px solid rgba(255, 234, 167, 0.2)' }}>
                <h3>🎯 Next Steps:</h3>
                <ul>
                    <li>Upload an image to generate homescreen visualizations</li>
                    <li>Select from available screen types (Security, Entertainment, Smart Home)</li>
                    <li>View and manage your visualization results</li>
                    <li>Explore the admin panel at <a href="/admin" target="_blank" style={{ color: 'var(--gold-primary)' }}>/admin</a></li>
                </ul>
            </div>
        </div>
    );
};

export default DashboardPage;
