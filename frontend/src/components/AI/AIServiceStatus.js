import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import './AIServiceStatus.css';

const AIServiceStatus = ({ onServiceSelect }) => {
  const [aiStatus, setAiStatus] = useState(null);
  const [providers, setProviders] = useState({});
  const [health, setHealth] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedProvider, setSelectedProvider] = useState('mock_ai');

  useEffect(() => {
    fetchAIServiceData();
    // Refresh data every 30 seconds
    const interval = setInterval(fetchAIServiceData, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchAIServiceData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch AI service status
      const statusResponse = await fetch('/api/ai-services/status/', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          'Content-Type': 'application/json',
        },
      });

      if (!statusResponse.ok) {
        throw new Error('Failed to fetch AI service status');
      }

      const statusData = await statusResponse.json();
      setAiStatus(statusData);

      // Fetch providers information
      const providersResponse = await fetch('/api/ai-services/providers/', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          'Content-Type': 'application/json',
        },
      });

      if (!providersResponse.ok) {
        throw new Error('Failed to fetch providers information');
      }

      const providersData = await providersResponse.json();
      setProviders(providersData);

      // Fetch health information
      const healthResponse = await fetch('/api/ai-services/health/', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          'Content-Type': 'application/json',
        },
      });

      if (!healthResponse.ok) {
        throw new Error('Failed to fetch health information');
      }

      const healthData = await healthResponse.json();
      setHealth(healthData);

    } catch (err) {
      console.error('Error fetching AI service data:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleProviderSelect = (providerName) => {
    setSelectedProvider(providerName);
    if (onServiceSelect) {
      onServiceSelect(providerName);
    }
  };

  const getStatusColor = (status) => {
    switch (status?.toLowerCase()) {
      case 'healthy':
      case 'operational':
      case 'active':
        return 'green';
      case 'degraded':
      case 'warning':
        return 'orange';
      case 'unhealthy':
      case 'failed':
      case 'error':
        return 'red';
      default:
        return 'gray';
    }
  };

  const formatServiceType = (serviceType) => {
    return serviceType.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  if (loading && !aiStatus) {
    return (
      <div className="ai-service-status loading">
        <div className="loading-spinner"></div>
        <p>Loading AI service information...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="ai-service-status error">
        <h3>AI Services Status</h3>
        <div className="error-message">
          <p>Error loading AI service information: {error}</p>
          <button onClick={fetchAIServiceData} className="retry-button">
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="ai-service-status">
      <div className="status-header">
        <h3>AI Services Status</h3>
        <button 
          onClick={fetchAIServiceData} 
          className="refresh-button"
          disabled={loading}
        >
          {loading ? '⟳' : '↻'} Refresh
        </button>
      </div>

      {/* Overall Status */}
      {aiStatus && (
        <div className="overall-status">
          <h4>Overall Status</h4>
          <div className="status-grid">
            <div className="status-item">
              <span className="label">Total Providers:</span>
              <span className="value">{aiStatus.registry_status?.total_providers || 0}</span>
            </div>
            <div className="status-item">
              <span className="label">Available Services:</span>
              <span className="value">{aiStatus.factory_status?.total_available_services || 0}</span>
            </div>
          </div>
        </div>
      )}

      {/* Service Types */}
      {aiStatus?.registry_status?.providers_by_service && (
        <div className="service-types">
          <h4>Services by Type</h4>
          <div className="service-type-grid">
            {Object.entries(aiStatus.registry_status.providers_by_service).map(([serviceType, count]) => (
              <div key={serviceType} className="service-type-item">
                <span className="service-type">{formatServiceType(serviceType)}</span>
                <span className="provider-count">{count} provider{count !== 1 ? 's' : ''}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Providers */}
      <div className="providers-section">
        <h4>Available Providers</h4>
        <div className="providers-grid">
          {Object.entries(providers).map(([providerName, providerInfo]) => (
            <div 
              key={providerName} 
              className={`provider-card ${selectedProvider === providerName ? 'selected' : ''}`}
              onClick={() => handleProviderSelect(providerName)}
            >
              <div className="provider-header">
                <h5>{providerName}</h5>
                <div 
                  className="status-indicator"
                  style={{ backgroundColor: getStatusColor(health[providerName]?.status) }}
                  title={health[providerName]?.status || 'Unknown'}
                ></div>
              </div>
              
              <div className="provider-details">
                <div className="detail-item">
                  <span className="label">Services:</span>
                  <span className="value">
                    {providerInfo.available_services?.join(', ') || 'None'}
                  </span>
                </div>
                
                {providerInfo.provider_info && (
                  <>
                    <div className="detail-item">
                      <span className="label">Status:</span>
                      <span className="value">{providerInfo.provider_info.status || 'Unknown'}</span>
                    </div>
                    
                    {providerInfo.provider_info.total_requests !== undefined && (
                      <div className="detail-item">
                        <span className="label">Total Requests:</span>
                        <span className="value">{providerInfo.provider_info.total_requests}</span>
                      </div>
                    )}
                  </>
                )}
              </div>

              {/* Health Details */}
              {health[providerName] && (
                <div className="health-details">
                  <div className="health-item">
                    <span className="label">Health:</span>
                    <span 
                      className="value"
                      style={{ color: getStatusColor(health[providerName].status) }}
                    >
                      {health[providerName].status}
                    </span>
                  </div>
                  
                  {health[providerName].request_stats && (
                    <div className="health-item">
                      <span className="label">Requests:</span>
                      <span className="value">
                        {Object.values(health[providerName].request_stats).reduce((a, b) => a + b, 0)}
                      </span>
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Selected Provider Info */}
      {selectedProvider && providers[selectedProvider] && (
        <div className="selected-provider-info">
          <h4>Selected Provider: {selectedProvider}</h4>
          <p>This provider will be used for AI-enhanced image processing.</p>
          
          {providers[selectedProvider].available_services && (
            <div className="available-services">
              <strong>Available Services:</strong>
              <ul>
                {providers[selectedProvider].available_services.map(service => (
                  <li key={service}>{formatServiceType(service)}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      <div className="status-footer">
        <small>
          Last updated: {aiStatus ? new Date(aiStatus.timestamp * 1000).toLocaleTimeString() : 'Never'}
        </small>
      </div>
    </div>
  );
};

AIServiceStatus.propTypes = {
  onServiceSelect: PropTypes.func
};

export default AIServiceStatus;
