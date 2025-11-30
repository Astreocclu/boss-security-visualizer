import React, { useState, useEffect } from 'react';
import { Link, useParams, useNavigate } from 'react-router-dom';
import {
  getVisualizationRequestById,
  regenerateVisualizationRequest,
  generateAudit,
  getAuditReport
} from '../services/api';
import './ResultDetailPage.css';

import Skeleton from '../components/Common/Skeleton';
import AuditResults from '../features/audit/AuditResults';
import ProcessingScreen from '../components/ProcessingScreen';

const ResultDetailPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const sliderRef = React.useRef(null);

  const [request, setRequest] = useState(null);
  const [auditReport, setAuditReport] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isRegenerating, setIsRegenerating] = useState(false);
  const [showOriginal, setShowOriginal] = useState(true); // Magic Flip State

  useEffect(() => {
    const fetchRequestDetails = async () => {
      try {
        const data = await getVisualizationRequestById(id);
        setRequest(data);
        setError(null);

        if (data.status === 'complete' || data.status === 'failed') {
          setIsLoading(false);
          setIsRegenerating(false);

          // Trigger or fetch audit if complete
          if (data.status === 'complete') {
            fetchAudit(id);
          }

          return true; // Stop polling
        }
      } catch (err) {
        console.error(`Error fetching visualization request #${id}:`, err);
        if (err.response?.status === 404) {
          setError(`Visualization request #${id} not found.`);
          return true;
        } else {
          if (isLoading) {
            setError('Failed to load visualization request details. Please try again later.');
          }
        }
      } finally {
        if (!isRegenerating) {
          setIsLoading(false);
        }
      }
      return false; // Continue polling
    };

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
  }, [id, isRegenerating]);

  const fetchAudit = async (requestId) => {
    try {
      // Try to get existing report
      const report = await getAuditReport(requestId);
      setAuditReport(report);
    } catch (err) {
      // If not found, generate it
      if (err.status === 404) {
        try {
          const newReport = await generateAudit(requestId);
          setAuditReport(newReport);
        } catch (genErr) {
          console.error("Failed to generate audit:", genErr);
        }
      }
    }
  };

  const handleRegenerate = async () => {
    try {
      setIsRegenerating(true);
      await regenerateVisualizationRequest(id);
      // Polling will pick up the status change
    } catch (err) {
      console.error('Failed to regenerate:', err);
      setError('Failed to start regeneration. Please try again.');
      setIsRegenerating(false);
    }
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
  const qualityScore = resultImage?.metadata?.quality_score || 0;

  const getScoreColorClass = (score) => {
    if (score >= 90) return 'high';
    if (score >= 70) return 'medium';
    return 'low';
  };

  // Granular Progress Bar Logic
  const steps = [
    { label: 'Analyzing', percent: 10 },
    { label: 'Cleaning', percent: 30 },
    { label: 'Building', percent: 50 },
    { label: 'Checking', percent: 80 } // Shared by Checking light/quality
  ];

  const currentProgress = request?.progress_percentage || 0;
  const currentStatusMessage = request?.status_message || '';

  // Determine active step index based on progress or message
  let activeStepIndex = 0;
  if (currentProgress >= 80 || currentStatusMessage.toLowerCase().includes('checking')) {
    activeStepIndex = 3;
  } else if (currentProgress >= 50 || currentStatusMessage.toLowerCase().includes('building')) {
    activeStepIndex = 2;
  } else if (currentProgress >= 30 || currentStatusMessage.toLowerCase().includes('cleaning')) {
    activeStepIndex = 1;
  } else {
    activeStepIndex = 0;
  }

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

      {request.status === 'complete' && (
        <>
          <div className="quality-score-section">
            <div className={`score-circle ${getScoreColorClass(Math.round(qualityScore * 100))}`}>
              <span className="score-value">{Math.round(qualityScore * 100)}%</span>
            </div>
            <div className="score-label">AI Quality Score</div>

            {resultImage?.metadata?.quality_reason && (
              <div className="quality-reason">
                <strong>AI Analysis:</strong> {resultImage.metadata.quality_reason}
              </div>
            )}

            <p className="text-muted mt-2">
              Based on AI analysis of realism, installation accuracy, and image clarity.
            </p>
          </div>

          {/* New Audit Section */}
          <AuditResults auditReport={auditReport} />
        </>
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
