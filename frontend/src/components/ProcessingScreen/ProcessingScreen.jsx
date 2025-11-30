import { useState, useEffect, useRef, useCallback } from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';
import './ProcessingScreen.css';

const SALES_MESSAGES = [
  "Initializing Nano Banana Pro Architecture...",
  "Scanning architectural geometry & light paths...",
  "Detecting vulnerabilities & ground-level entry points...",
  "Removing visual clutter (hoses, trash cans)...",
  "Fabricating 12x12 Stainless Steel Security Mesh...",
  "Calibrating final lighting and shadow render...",
];

const FACTS = [
  { highlight: "17,000+", rest: " screens installed. Zero break-ins. Ever." },
  { highlight: "66%", rest: " of solar heat blocked, reducing energy costs." },
  { highlight: "100 ft-lbs", rest: " of impact force protection per screen." },
  { highlight: "Marine-grade", rest: " stainless steel that never rusts or corrodes." },
  { highlight: "15 year", rest: " comprehensive warranty on all Boss Security Screens." },
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
  const [messageIndex, setMessageIndex] = useState(0);
  const [messageFading, setMessageFading] = useState(false);
  const lastBackendProgress = useRef(backendProgress);
  const animationFrame = useRef(null);
  const startTimeRef = useRef(null);

  // Performance logger - capture start time on mount
  useEffect(() => {
    startTimeRef.current = performance.now();
    return () => {
      startTimeRef.current = null;
    };
  }, []);

  // Smooth, slow progress animation between backend updates
  useEffect(() => {
    const targetProgress = Math.min(backendProgress + 5, 95);

    const animate = () => {
      setDisplayProgress(prev => {
        // Never go backwards, never exceed target
        if (prev >= targetProgress) return prev;

        // Slower, steadier increment (reduced from 0.05 to 0.015)
        const increment = Math.max(0.05, (targetProgress - prev) * 0.015);
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

  // Jump to 100% on complete and log performance
  useEffect(() => {
    if (status === 'complete') {
      setDisplayProgress(100);
      // Performance logger - log completion time
      if (startTimeRef.current) {
        const endTime = performance.now();
        const duration = (endTime - startTimeRef.current) / 1000;
        console.log(`⏱️ VISUALIZATION TIME: ${duration.toFixed(2)} seconds`); // eslint-disable-line no-console
      }
      if (onComplete) onComplete();
    } else if (status === 'failed') {
      if (onError) onError(statusMessage || 'Processing failed');
    }
  }, [status, onComplete, onError, statusMessage]);

  // Rotate sales messages every 8 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      setMessageFading(true);
      setTimeout(() => {
        setMessageIndex(prev => (prev + 1) % SALES_MESSAGES.length);
        setMessageFading(false);
      }, 400);
    }, 8000);

    return () => clearInterval(interval);
  }, []);

  // Rotate facts every 10 seconds (offset from messages)
  useEffect(() => {
    const interval = setInterval(() => {
      setFactFading(true);
      setTimeout(() => {
        setCurrentFactIndex(prev => (prev + 1) % FACTS.length);
        setFactFading(false);
      }, 400);
    }, 10000);

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
  const currentMessage = SALES_MESSAGES[messageIndex];

  return (
    <div className="processing-screen">
      <div className="processing-container">
        {/* Radar Animation */}
        <div className="radar-section">
          <div className="radar-container">
            <div className="radar-ring radar-ring-1" />
            <div className="radar-ring radar-ring-2" />
            <div className="radar-ring radar-ring-3" />
            <div className="radar-core" />
            {originalImageUrl && (
              <img
                src={originalImageUrl}
                alt="Your home"
                className="radar-image"
              />
            )}
          </div>
        </div>

        {/* Sales Message */}
        <h2 className={`sales-message ${messageFading ? 'fading' : ''}`}>
          {currentMessage}
        </h2>

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
