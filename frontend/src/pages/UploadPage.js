import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Check } from 'lucide-react';
import { createVisualizationRequest } from '../services/api';
import useVisualizationStore from '../store/visualizationStore';
import Step4Upload from '../components/UploadWizard/Step4Upload';
import Step2Scope from '../components/UploadWizard/Step2Scope';
import Step3Customization from '../components/UploadWizard/Step3Customization';
import Step5Review from '../components/UploadWizard/Step5Review';
import './UploadPage.css';

const UploadPage = () => {
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState({
    meshChoice: '12x12',
    frameColor: 'Black',
    meshColor: 'Black',
    image: null
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const navigate = useNavigate();
  const { scope } = useVisualizationStore();

  const nextStep = () => setStep(prev => prev + 1);
  const prevStep = () => setStep(prev => prev - 1);

  const handleSubmit = async () => {
    setIsSubmitting(true);
    setError(null);
    try {
      const data = new FormData();
      // Include scope data
      const scopePayload = {
        windows: scope.hasWindows,
        doors: scope.hasDoors,
        patio: scope.hasPatio
      };
      data.append('scope', JSON.stringify(scopePayload));
      data.append('mesh_choice', formData.meshChoice);
      data.append('frame_color', formData.frameColor);
      data.append('mesh_color', formData.meshColor);
      data.append('original_image', formData.image);

      // Legacy fields for compatibility
      data.append('screen_type', 'window_fixed'); // Default
      data.append('mesh_type', formData.meshChoice);
      data.append('color', formData.frameColor);

      const response = await createVisualizationRequest(data);
      navigate(`/results/${response.id}`);
    } catch (err) {
      console.error(err);
      setError('Failed to create request. Please try again.');
      setIsSubmitting(false);
    }
  };

  return (
    <div className="upload-page">
      <div className="wizard-progress-bar">
        <div className="progress-track">
          <div
            className="progress-fill"
            style={{ width: `${((step - 1) / 3) * 100}%` }}
          />
        </div>
        <div className="steps-indicator">
          {[1, 2, 3, 4].map(s => (
            <div
              key={s}
              className={`step-dot ${s <= step ? 'active' : ''} ${s === step ? 'current' : ''}`}
            >
              {s < step ? <Check size={12} /> : s}
            </div>
          ))}
        </div>
      </div>

      {step === 1 && (
        <Step4Upload
          formData={formData}
          setFormData={setFormData}
          nextStep={nextStep}
          prevStep={prevStep}
        />
      )}
      {step === 2 && (
        <Step2Scope
          nextStep={nextStep}
          prevStep={prevStep}
        />
      )}
      {step === 3 && (
        <Step3Customization
          formData={formData}
          setFormData={setFormData}
          nextStep={nextStep}
          prevStep={prevStep}
        />
      )}
      {step === 4 && (
        <Step5Review
          formData={formData}
          scope={scope}
          prevStep={prevStep}
          handleSubmit={handleSubmit}
          isSubmitting={isSubmitting}
          error={error}
        />
      )}
    </div>
  );
};

export default UploadPage;
