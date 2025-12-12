import { useState, useEffect, useCallback } from 'react';
import { Link, useParams, useSearchParams } from 'react-router-dom';
import { Shield, Download } from 'lucide-react';
import {
  getVisualizationRequestById,
  regenerateVisualizationRequest,
  getAuditReport
} from '../services/api';
import './ResultDetailPage.css';

import Skeleton from '../components/Common/Skeleton';
import ProcessingScreen from '../components/ProcessingScreen';
import LeadCaptureModal from '../components/LeadCaptureModal';

const ResultDetailPage = () => {
  const { id } = useParams();
  const [searchParams] = useSearchParams();

  const [request, setRequest] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isRegenerating, setIsRegenerating] = useState(false);
  const [showOriginal, setShowOriginal] = useState(true);
  const [auditReport, setAuditReport] = useState(null);
  const [showLeadModal, setShowLeadModal] = useState(false);

  // Detect sales rep mode
  const isSalesRep = searchParams.get('rep') === 'true';

  const fetchRequestDetails = useCallback(async () => {
    try {
      const data = await getVisualizationRequestById(id);
      setRequest(data);
      setError(null);

      if (data.status === 'complete' || data.status === 'failed') {
        setIsLoading(false);
        setIsRegenerating(false);

        // Fetch audit report if complete
        if (data.status === 'complete' && !auditReport) {
          try {
            const audit = await getAuditReport(id);
            setAuditReport(audit);
          } catch (auditErr) {
            // Audit may not exist yet, that's OK
            console.log('Audit not available:', auditErr);
          }
        }

        return true; // Stop polling
      }
    } catch (err) {
      console.error(`Error fetching visualization request #${id}:`, err);
      if (err.status === 404 || err.response?.status === 404) {
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
  }, [id, isRegenerating, auditReport]);

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

  // Guard against null request
  if (!request) {
    return null;
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

  // Get vulnerability count from audit
  const vulnerabilityCount = auditReport?.vulnerabilities?.length || 0;

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

      <div className="comparison-slider-container">
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

      {/* AI Enhancement Disclaimer */}
      {request.status === 'complete' && (
        <p className="ai-disclaimer">
          AI-enhanced visualization. Lighting and weather conditions may vary from actual appearance.
        </p>
      )}

      {/* Simplified Security Teaser + CTA */}
      {request.status === 'complete' && (
        <div className="security-report-teaser">
          <div className="teaser-content">
            <Shield size={32} className="teaser-icon" />
            <div className="teaser-text">
              <h3>
                {vulnerabilityCount > 0
                  ? `${vulnerabilityCount} Security Vulnerabilit${vulnerabilityCount === 1 ? 'y' : 'ies'} Detected`
                  : 'Security Analysis Complete'}
              </h3>
              <p>
                Your free security assessment reveals what intruders see when they look at your home—and exactly how to stop them.
              </p>
            </div>
          </div>
          <button
            className="btn-download-report"
            onClick={() => {
              if (isSalesRep) {
                // Sales reps skip lead capture, go direct to PDF
                window.open(`/api/visualization/${id}/pdf/`, '_blank');
              } else {
                setShowLeadModal(true);
              }
            }}
          >
            <Download size={20} />
            Download Your Free Security Report
          </button>
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

      {/* Lead Capture Modal */}
      <LeadCaptureModal
        isOpen={showLeadModal}
        onClose={() => setShowLeadModal(false)}
        visualizationId={id}
        isSalesRep={isSalesRep}
      />
    </div>
  );
};

export default ResultDetailPage;
