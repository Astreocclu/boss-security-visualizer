import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Check } from 'lucide-react';
import { createVisualizationRequest } from '../services/api';
import Step1Categories from '../components/UploadWizard/Step1Categories';
import Step2Mesh from '../components/UploadWizard/Step2Mesh';
import Step3Customization from '../components/UploadWizard/Step3Customization';
import Step4Upload from '../components/UploadWizard/Step4Upload';
import Step5Review from '../components/UploadWizard/Step5Review';
import './UploadPage.css';

const UploadPage = () => {
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState({
    categories: [],
    meshChoice: '12x12',
    frameColor: 'Black',
    meshColor: 'Black',
    image: null
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const nextStep = () => setStep(prev => prev + 1);
  const prevStep = () => setStep(prev => prev - 1);

  const handleSubmit = async () => {
    setIsSubmitting(true);
    setError(null);
    try {
      const data = new FormData();
      data.append('screen_categories', JSON.stringify(formData.categories));
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
            style={{ width: `${((step - 1) / 4) * 100}%` }}
          />
        </div>
        <div className="steps-indicator">
          {[1, 2, 3, 4, 5].map(s => (
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
        <Step1Categories
          formData={formData}
          setFormData={setFormData}
          nextStep={nextStep}
        />
      )}
      {step === 2 && (
        <Step2Mesh
          formData={formData}
          setFormData={setFormData}
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
        <Step4Upload
          formData={formData}
          setFormData={setFormData}
          nextStep={nextStep}
          prevStep={prevStep}
        />
      )}
      {step === 5 && (
        <Step5Review
          formData={formData}
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
