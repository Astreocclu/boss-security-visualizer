import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import ScreenSelector from '../components/Upload/ScreenSelector';
import ImageUploader from '../components/Upload/ImageUploader';
import AIServiceStatus from '../components/AI/AIServiceStatus';
import { createVisualizationRequest } from '../services/api';

const UploadPage = () => {
  const [selectedScreenTypeId, setSelectedScreenTypeId] = useState(null);
  const [selectedImage, setSelectedImage] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [selectedAIProvider, setSelectedAIProvider] = useState('mock_ai');
  const navigate = useNavigate();

  const handleScreenTypeSelect = (screenTypeId) => {
    setSelectedScreenTypeId(screenTypeId);
  };

  const handleImageSelect = (file) => {
    setSelectedImage(file);
  };

  const handleAIProviderSelect = (providerName) => {
    setSelectedAIProvider(providerName);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Validate form inputs
    if (!selectedScreenTypeId) {
      setError('Please select a screen type');
      return;
    }

    if (!selectedImage) {
      setError('Please select an image');
      return;
    }

    setError(null);
    setIsSubmitting(true);

    try {
      // Create FormData object for the multipart/form-data request
      const formData = new FormData();
      formData.append('screen_type', selectedScreenTypeId);
      formData.append('image', selectedImage);
      // Note: AI provider selection is handled on the backend based on availability

      // Send the request to the API
      const response = await createVisualizationRequest(formData);

      // Navigate to the results page or the specific result detail page
      navigate(`/results/${response.id}`);
    } catch (err) {
      console.error('Error creating visualization request:', err);
      setError(err.response?.data?.detail || 'Failed to create visualization request. Please try again.');
      setIsSubmitting(false);
    }
  };

  return (
    <div className="upload-page">
      <h1>Upload Image for AI-Enhanced Visualization</h1>

      {/* AI Service Status */}
      <div className="form-section">
        <h2>AI Services Status</h2>
        <AIServiceStatus onServiceSelect={handleAIProviderSelect} />
      </div>

      <form onSubmit={handleSubmit}>
        <div className="form-section">
          <h2>Step 1: Select Screen Type</h2>
          <ScreenSelector
            onSelect={handleScreenTypeSelect}
            selectedScreenTypeId={selectedScreenTypeId}
          />
        </div>

        <div className="form-section">
          <h2>Step 2: Upload Image</h2>
          <ImageUploader onImageSelect={handleImageSelect} />
          <p className="ai-info">
            <strong>AI Enhancement:</strong> Your image will be processed using AI-powered window detection
            and realistic screen visualization. The selected AI provider ({selectedAIProvider}) will be used
            for enhanced quality and realism.
          </p>
        </div>

        {error && <div className="error-message">{error}</div>}

        <div className="form-actions">
          <button
            type="submit"
            className="submit-button"
            disabled={isSubmitting || !selectedScreenTypeId || !selectedImage}
          >
            {isSubmitting ? 'Processing with AI...' : 'Generate AI Visualization'}
          </button>

          <Link to="/results" className="view-results-link">
            View All Results
          </Link>
        </div>
      </form>
    </div>
  );
};

export default UploadPage;
