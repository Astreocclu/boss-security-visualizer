import React from 'react';

const ResultsDisplay = ({ originalImage, resultImage, status }) => {
  return (
    <div className="results-display">
      <div className="images-container">
        <div className="image-card">
          <h3>Original Image</h3>
          {originalImage ? (
            <img 
              src={originalImage} 
              alt="Original" 
              className="result-image"
            />
          ) : (
            <div className="image-placeholder">
              No image available
            </div>
          )}
        </div>
        
        <div className="image-card">
          <h3>Visualization Result</h3>
          {status === 'complete' && resultImage ? (
            <img 
              src={resultImage} 
              alt="Result" 
              className="result-image"
            />
          ) : status === 'processing' ? (
            <div className="processing-indicator">
              <div className="spinner"></div>
              <p>Processing...</p>
            </div>
          ) : status === 'failed' ? (
            <div className="error-indicator">
              <p>Processing failed</p>
            </div>
          ) : (
            <div className="image-placeholder">
              No result available
            </div>
          )}
        </div>
      </div>
      
      <div className="status-indicator">
        <p>
          Status: <span className={`status-${status}`}>{status}</span>
        </p>
      </div>
    </div>
  );
};

export default ResultsDisplay;
