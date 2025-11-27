import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { getVisualizationRequests } from '../services/api';
import './ResultsPage.css';

import Skeleton from '../components/Common/Skeleton';

const ResultsPage = () => {
  const [requests, setRequests] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchRequests = async () => {
      try {
        setIsLoading(true);
        const data = await getVisualizationRequests();
        setRequests(data.results || data);
        setError(null);
      } catch (err) {
        console.error('Error fetching visualization requests:', err);
        setError('Failed to load visualization requests. Please try again later.');
      } finally {
        setIsLoading(false);
      }
    };

    fetchRequests();
  }, []);

  if (isLoading) {
    return (
      <div className="results-page">
        <h1>Visualization Results</h1>
        <div className="results-actions">
          <Skeleton width={150} height={40} />
        </div>
        <div className="results-list">
          {[1, 2, 3, 4, 5, 6].map((n) => (
            <div key={n} className="result-item" style={{ pointerEvents: 'none' }}>
              <div className="result-thumbnail">
                <Skeleton variant="rectangular" height="100%" animation="wave" />
              </div>
              <div className="result-info">
                <Skeleton variant="text" width="60%" height={24} style={{ marginBottom: '10px' }} />
                <div className="status-row" style={{ display: 'flex', gap: '10px', marginBottom: '10px' }}>
                  <Skeleton variant="rectangular" width={80} height={24} style={{ borderRadius: '12px' }} />
                  <Skeleton variant="text" width={100} />
                </div>
                <Skeleton variant="text" width="40%" />
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="results-page error">
        <h1>Results</h1>
        <div className="error-message">{error}</div>
        <p>
          <Link to="/upload">Upload New Image</Link>
        </p>
      </div>
    );
  }

  return (
    <div className="results-page">
      <h1>Visualization Results</h1>

      <div className="results-actions">
        <Link to="/upload" className="upload-button">Upload New Image</Link>
      </div>

      {requests.length === 0 ? (
        <div className="no-results">
          <p>No visualization requests found.</p>
          <p>Upload an image to create your first visualization.</p>
        </div>
      ) : (
        <div className="results-list">
          {requests.map((request) => (
            <Link to={`/results/${request.id}`} key={request.id} className="result-item-link">
              <div className="result-item">
                <div className="result-thumbnail">
                  {request.latest_result_url ? (
                    <div className="thumbnail-wrapper">
                      <img
                        src={request.latest_result_url}
                        alt="Generated Result"
                        className="thumbnail-image"
                      />
                      <span className="thumbnail-badge">After</span>
                    </div>
                  ) : request.original_image_url ? (
                    <div className="thumbnail-wrapper">
                      <img
                        src={request.original_image_url}
                        alt="Original"
                        className="thumbnail-image"
                      />
                      <span className="thumbnail-badge original">Before</span>
                    </div>
                  ) : (
                    <div className="thumbnail-placeholder">No Image</div>
                  )}
                </div>

                <div className="result-info">
                  <h3>Request #{request.id}</h3>
                  <div className="status-row">
                    <span className={`status-badge status-${request.status}`}>
                      {request.status}
                    </span>
                    <span className="date">{new Date(request.created_at).toLocaleDateString()}</span>
                  </div>
                  <p className="screen-type">
                    {request.screen_type_name || 'Standard Screen'}
                  </p>
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
};

export default ResultsPage;
