import React, { useState, useEffect, useRef, useCallback } from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';
import './ProcessingScreen.css';

const STAGE_MESSAGES = [
  { max: 15, message: "Analyzing your home's architecture..." },
  { max: 30, message: "Detecting windows and entry points..." },
  { max: 45, message: "Preparing image for visualization..." },
  { max: 70, message: "Rendering security screens..." },
  { max: 85, message: "Applying realistic shadows and lighting..." },
  { max: 100, message: "Running final quality check..." },
];

const FACTS = [
  { highlight: "17,000+", rest: " screens installed. Zero break-ins. Ever." },
  { highlight: "66%", rest: " of solar heat blocked, reducing energy costs." },
  { highlight: "100 ft-lbs", rest: " of impact force protection per screen." },
  { highlight: "Marine-grade", rest: " stainless steel that never rusts or corrodes." },
  { highlight: "25 year", rest: " warranty on all Boss Security Screens." },
];

const ProcessingScreen = ({
  visualizationId,
  originalImageUrl,
  backendProgress = 0,
  statusMessage = '',
  status = 'processing',
  onComplete,
  onError,
  onRetry,
}) => {
  const [displayProgress, setDisplayProgress] = useState(0);
  const [currentFactIndex, setCurrentFactIndex] = useState(0);
  const [factFading, setFactFading] = useState(false);
  const [stageMessage, setStageMessage] = useState(STAGE_MESSAGES[0].message);
  const [stageFading, setStageFading] = useState(false);
  const lastBackendProgress = useRef(backendProgress);
  const animationFrame = useRef(null);

  // Smooth progress animation between backend updates
  useEffect(() => {
    const targetProgress = Math.min(backendProgress + 10, 95);

    const animate = () => {
      setDisplayProgress(prev => {
        // Never go backwards, never exceed target
        if (prev >= targetProgress) return prev;

        // Smooth increment
        const increment = Math.max(0.1, (targetProgress - prev) * 0.05);
        const next = Math.min(prev + increment, targetProgress);

        if (next < targetProgress) {
          animationFrame.current = requestAnimationFrame(animate);
        }
        return next;
      });
    };

    // When backend progress jumps, update smoothly
    if (backendProgress > lastBackendProgress.current) {
      lastBackendProgress.current = backendProgress;
      animationFrame.current = requestAnimationFrame(animate);
    }

    return () => {
      if (animationFrame.current) {
        cancelAnimationFrame(animationFrame.current);
      }
    };
  }, [backendProgress]);

  // Jump to 100% on complete
  useEffect(() => {
    if (status === 'complete') {
      setDisplayProgress(100);
      if (onComplete) onComplete();
    } else if (status === 'failed') {
      if (onError) onError(statusMessage || 'Processing failed');
    }
  }, [status, onComplete, onError, statusMessage]);

  // Update stage message based on progress
  useEffect(() => {
    const stage = STAGE_MESSAGES.find(s => displayProgress <= s.max) || STAGE_MESSAGES[STAGE_MESSAGES.length - 1];
    if (stage.message !== stageMessage) {
      setStageFading(true);
      setTimeout(() => {
        setStageMessage(stage.message);
        setStageFading(false);
      }, 200);
    }
  }, [displayProgress, stageMessage]);

  // Rotate facts every 8 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      setFactFading(true);
      setTimeout(() => {
        setCurrentFactIndex(prev => (prev + 1) % FACTS.length);
        setFactFading(false);
      }, 400);
    }, 8000);

    return () => clearInterval(interval);
  }, []);

  const handleRetry = useCallback(() => {
    if (onRetry) {
      onRetry();
    } else {
      window.location.reload();
    }
  }, [onRetry]);

  // Error state
  if (status === 'failed') {
    return (
      <div className="processing-screen">
        <div className="processing-container">
          <div className="error-state">
            <div className="error-icon">
              <AlertTriangle size={48} />
            </div>
            <h2>Something went wrong</h2>
            <p className="error-message">
              {statusMessage || 'An unexpected error occurred during processing.'}
            </p>
            <button className="retry-button" onClick={handleRetry}>
              <RefreshCw size={18} />
              Try Again
            </button>
          </div>
          <div className="branding">
            Powered by <span className="brand-name">Boss Security Screens</span>
          </div>
        </div>
      </div>
    );
  }

  const currentFact = FACTS[currentFactIndex];

  return (
    <div className="processing-screen">
      <div className="processing-container">
        {/* Image with scan line */}
        <div className="image-section">
          {originalImageUrl ? (
            <div className="image-wrapper">
              <img
                src={originalImageUrl}
                alt="Your home"
                className="processing-image"
              />
              <div className="scan-line" />
              <div className="image-overlay" />
            </div>
          ) : (
            <div className="image-placeholder">
              <div className="placeholder-icon">🏠</div>
              <div className="scan-line" />
            </div>
          )}
        </div>

        {/* Progress section */}
        <div className="progress-section">
          <div className="progress-bar-container">
            <div
              className="progress-bar-fill"
              style={{ width: `${displayProgress}%` }}
            />
            <div className="progress-shimmer" />
          </div>
          <div className="progress-percentage">{Math.round(displayProgress)}%</div>
        </div>

        {/* Stage message */}
        <div className={`stage-message ${stageFading ? 'fading' : ''}`}>
          {stageMessage}
        </div>

        {/* Fact card */}
        <div className="fact-card">
          <div className="fact-label">Did you know?</div>
          <div className={`fact-content ${factFading ? 'fading' : ''}`}>
            <span className="fact-highlight">{currentFact.highlight}</span>
            <span className="fact-rest">{currentFact.rest}</span>
          </div>
        </div>

        {/* Branding */}
        <div className="branding">
          Powered by <span className="brand-name">Boss Security Screens</span>
        </div>
      </div>
    </div>
  );
};

export default ProcessingScreen;
