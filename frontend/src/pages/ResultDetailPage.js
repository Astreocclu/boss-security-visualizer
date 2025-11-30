import { useState, useEffect, useRef, useCallback } from 'react';
import { Link, useParams, useNavigate } from 'react-router-dom';
import { FileText } from 'lucide-react';
import {
  getVisualizationRequestById,
  regenerateVisualizationRequest
} from '../services/api';
import './ResultDetailPage.css';

import Skeleton from '../components/Common/Skeleton';
import ProcessingScreen from '../components/ProcessingScreen';

const ResultDetailPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const sliderRef = useRef(null);

  const [request, setRequest] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isRegenerating, setIsRegenerating] = useState(false);
  const [showOriginal, setShowOriginal] = useState(true);
  const [isGeneratingQuote, setIsGeneratingQuote] = useState(false);

  const fetchRequestDetails = useCallback(async () => {
    try {
      const data = await getVisualizationRequestById(id);
      setRequest(data);
      setError(null);

      if (data.status === 'complete' || data.status === 'failed') {
        setIsLoading(false);
        setIsRegenerating(false);
        return true; // Stop polling
      }
    } catch (err) {
      // eslint-disable-next-line no-console
      console.error(`Error fetching visualization request #${id}:`, err);
      if (err.response?.status === 404) {
        setError(`Visualization request #${id} not found.`);
        return true;
      } else {
        setError('Failed to load visualization request details. Please try again later.');
      }
    } finally {
      if (!isRegenerating) {
        setIsLoading(false);
      }
    }
    return false; // Continue polling
  }, [id, isRegenerating]);

  useEffect(() => {
    fetchRequestDetails();

    const pollInterval = setInterval(async () => {
      const shouldStop = await fetchRequestDetails();
      if (shouldStop) {
        clearInterval(pollInterval);
      }
    }, 3000);

    return () => {
      if (pollInterval) clearInterval(pollInterval);
    };
  }, [fetchRequestDetails]);

  const handleRegenerate = async () => {
    try {
      setIsRegenerating(true);
      await regenerateVisualizationRequest(id);
      // Polling will pick up the status change
    } catch (err) {
      // eslint-disable-next-line no-console
      console.error('Failed to regenerate:', err);
      setError('Failed to start regeneration. Please try again.');
      setIsRegenerating(false);
    }
  };

  const handleGenerateQuote = () => {
    setIsGeneratingQuote(true);
    setTimeout(() => {
      navigate('/quote/success', { state: { visualizationId: id } });
    }, 1500);
  };

  if (isLoading && !request) {
    return (
      <div className="result-detail-page">
        <div className="result-header">
          <div>
            <Skeleton variant="text" width={200} height={32} style={{ marginBottom: '10px' }} />
            <Skeleton variant="text" width={150} />
          </div>
          <Skeleton variant="rectangular" width={100} height={30} style={{ borderRadius: '15px' }} />
        </div>

        <div className="comparison-slider-container" style={{ backgroundColor: '#f0f0f0', border: 'none' }}>
          <Skeleton variant="rectangular" width="100%" height="100%" animation="wave" />
        </div>

        <div className="action-bar">
          <Skeleton variant="rectangular" width={120} height={40} style={{ borderRadius: '4px' }} />
          <Skeleton variant="rectangular" width={120} height={40} style={{ borderRadius: '4px' }} />
          <Skeleton variant="rectangular" width={120} height={40} style={{ borderRadius: '4px' }} />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="result-detail-page error">
        <h1>Error</h1>
        <div className="error-message">{error}</div>
        <Link to="/results" className="btn btn-secondary">Back to Results</Link>
      </div>
    );
  }

  const resultImage = request.results && request.results.length > 0 ? request.results[0] : null;
  const resultImageUrl = resultImage ? resultImage.generated_image_url : null;

  const currentProgress = request?.progress_percentage || 0;
  const currentStatusMessage = request?.status_message || '';

  // Show ProcessingScreen for pending/processing states
  const isProcessing = isRegenerating || request.status === 'processing' || request.status === 'pending';

  if (isProcessing) {
    return (
      <ProcessingScreen
        visualizationId={id}
        originalImageUrl={request.clean_image_url || request.original_image_url}
        backendProgress={currentProgress}
        statusMessage={currentStatusMessage}
        status={request.status}
        onRetry={handleRegenerate}
      />
    );
  }

  return (
    <div className="result-detail-page">
      <div className="result-header">
        <div>
          <h2>Visualization #{id}</h2>
          <span className="text-muted">{new Date(request.created_at).toLocaleString()}</span>
        </div>
        <div className={`status-badge status-${request.status}`}>
          {request.status}
        </div>
      </div>

      <div className="comparison-slider-container" ref={sliderRef}>
        {/* Press to Reveal Mode */}
        <div className="magic-flip-container">
          <div className={`image-layer ${showOriginal ? 'visible' : 'hidden'}`}>
            <img src={request.clean_image_url || request.original_image_url} alt="Original" />
            <span className="label before-label">Original</span>
          </div>
          <div className={`image-layer ${!showOriginal ? 'visible' : 'hidden'}`}>
            {resultImageUrl ? (
              <img src={resultImageUrl} alt="With Screens" />
            ) : (
              <div className="placeholder-image">Processing...</div>
            )}
            <span className="label after-label">Boss Security Screen</span>
          </div>

          <div className="toggle-button-container">
            <button
              className={`btn-toggle-view ${!showOriginal ? 'active' : ''}`}
              onClick={() => setShowOriginal(!showOriginal)}
            >
              {showOriginal ? 'Show Security Screens' : 'Show Original'}
            </button>
          </div>
        </div>
      </div>

      {/* Generate Quote CTA */}
      {request.status === 'complete' && (
        <div className="quote-cta-section">
          <button
            className="btn-generate-quote"
            onClick={handleGenerateQuote}
            disabled={isGeneratingQuote}
          >
            <FileText size={20} />
            {isGeneratingQuote ? 'Analyzing Dimensions...' : 'GENERATE OFFICIAL QUOTE'}
          </button>
        </div>
      )}

      {/* Loading Overlay */}
      {isGeneratingQuote && (
        <div className="quote-loading-overlay">
          <div className="quote-loading-content">
            <div className="quote-spinner" />
            <p>Analyzing Dimensions...</p>
          </div>
        </div>
      )}

      <div className="action-bar">
        <Link to="/results" className="btn btn-secondary">
          ← Back to Gallery
        </Link>

        <button onClick={handleRegenerate} className="btn btn-regenerate" disabled={isRegenerating}>
          ↻ Regenerate
        </button>

        <Link to="/upload" className="btn btn-primary">
          + New Upload
        </Link>
      </div>
    </div>
  );
};

export default ResultDetailPage;
