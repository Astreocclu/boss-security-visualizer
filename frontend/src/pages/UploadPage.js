import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { DoorOpen, Maximize, LayoutTemplate, ArrowRight, ArrowLeft, Check, Upload, Shield, Star } from 'lucide-react';
import ImageUploader from '../components/Upload/ImageUploader';
import { createVisualizationRequest } from '../services/api';
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

  const handleCategoryToggle = (category) => {
    setFormData(prev => {
      const newCategories = prev.categories.includes(category)
        ? prev.categories.filter(c => c !== category)
        : [...prev.categories, category];
      return { ...prev, categories: newCategories };
    });
  };

  const handleMeshSelect = (mesh) => {
    setFormData(prev => ({ ...prev, meshChoice: mesh }));
  };

  const handleColorSelect = (type, color) => {
    setFormData(prev => ({ ...prev, [type]: color }));
  };

  const handleImageSelect = (file) => {
    setFormData(prev => ({ ...prev, image: file }));
  };

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

  const renderStep1 = () => (
    <div className="wizard-step fade-in">
      <div className="step-header">
        <h2>What are we screening?</h2>
        <p className="step-subtitle">Select all that apply to your project</p>
      </div>

      <div className="card-grid">
        {[
          { id: 'Window', icon: Maximize, label: 'Windows' },
          { id: 'Door', icon: DoorOpen, label: 'Doors' },
          { id: 'Patio', icon: LayoutTemplate, label: 'Patio / Sliding' }
        ].map(cat => {
          const Icon = cat.icon;
          const isSelected = formData.categories.includes(cat.id);
          return (
            <div
              key={cat.id}
              className={`icon-tile ${isSelected ? 'selected' : ''}`}
              onClick={() => handleCategoryToggle(cat.id)}
            >
              <div className="icon-wrapper">
                <Icon size={48} strokeWidth={1.5} />
              </div>
              <h3>{cat.label}</h3>
              {isSelected && <div className="check-badge"><Check size={16} /></div>}
            </div>
          );
        })}
      </div>

      <div className="wizard-actions right">
        <button
          className="btn-next"
          onClick={nextStep}
          disabled={formData.categories.length === 0}
        >
          Next Step <ArrowRight size={18} />
        </button>
      </div>
    </div>
  );

  const renderStep2 = () => (
    <div className="wizard-step fade-in">
      <div className="step-header">
        <h2>Select Protection Level</h2>
        <p className="step-subtitle">Choose the mesh strength for your screens</p>
      </div>

      <div className="radio-card-grid">
        {[
          {
            id: '10x10',
            label: '10x10 Standard',
            desc: 'Heavy Duty Protection',
            icon: Shield
          },
          {
            id: '12x12',
            label: '12x12 Security',
            desc: 'Enhanced Security Mesh',
            icon: Shield
          },
          {
            id: '12x12_american',
            label: '12x12 American',
            desc: 'Premium Marine Grade',
            badge: 'Best Value',
            icon: Star
          }
        ].map(mesh => {
          const Icon = mesh.icon;
          const isSelected = formData.meshChoice === mesh.id;
          return (
            <div
              key={mesh.id}
              className={`radio-card ${isSelected ? 'selected' : ''}`}
              onClick={() => handleMeshSelect(mesh.id)}
            >
              {mesh.badge && <div className="badge-best-value">{mesh.badge}</div>}
              <div className="radio-content">
                <div className="radio-icon">
                  <Icon size={32} strokeWidth={1.5} />
                </div>
                <div className="radio-text">
                  <h3>{mesh.label}</h3>
                  <p>{mesh.desc}</p>
                </div>
                <div className="radio-indicator">
                  <div className="radio-inner" />
                </div>
              </div>
            </div>
          );
        })}
      </div>

      <div className="wizard-actions">
        <button className="btn-back" onClick={prevStep}>
          <ArrowLeft size={18} /> Back
        </button>
        <button className="btn-next" onClick={nextStep}>
          Next Step <ArrowRight size={18} />
        </button>
      </div>
    </div>
  );

  const renderStep3 = () => (
    <div className="wizard-step fade-in">
      <div className="step-header">
        <h2>Customize Your Look</h2>
        <p className="step-subtitle">Match your home's aesthetic</p>
      </div>

      <div className="customization-section">
        <h3>Frame Color</h3>
        <div className="color-swatches-grid">
          {[
            { id: 'Black', hex: '#000000' },
            { id: 'Dark Bronze', hex: '#4B3621' },
            { id: 'Stucco', hex: '#9F9080' },
            { id: 'White', hex: '#FFFFFF', border: true },
            { id: 'Almond', hex: '#EADDcF' }
          ].map(color => (
            <div
              key={color.id}
              className={`swatch-container ${formData.frameColor === color.id ? 'selected' : ''}`}
              onClick={() => handleColorSelect('frameColor', color.id)}
            >
              <div
                className="color-swatch-circle"
                style={{
                  backgroundColor: color.hex,
                  border: color.border ? '1px solid #ccc' : 'none'
                }}
              />
              <span className="swatch-label">{color.id}</span>
            </div>
          ))}
        </div>
      </div>

      <div className="customization-section">
        <h3>Mesh Color</h3>
        <div className="color-swatches-grid">
          {[
            { id: 'Black', hex: '#000000', recommended: true },
            { id: 'Stucco', hex: '#9F9080' },
            { id: 'Bronze', hex: '#CD7F32' }
          ].map(color => (
            <div
              key={color.id}
              className={`swatch-container ${formData.meshColor === color.id ? 'selected' : ''}`}
              onClick={() => handleColorSelect('meshColor', color.id)}
            >
              <div
                className="color-swatch-circle"
                style={{ backgroundColor: color.hex }}
              />
              <span className="swatch-label">
                {color.id}
                {color.recommended && <span className="recommended-tag">Recommended</span>}
              </span>
            </div>
          ))}
        </div>
      </div>

      <div className="wizard-actions">
        <button className="btn-back" onClick={prevStep}>
          <ArrowLeft size={18} /> Back
        </button>
        <button className="btn-next" onClick={nextStep}>
          Next Step <ArrowRight size={18} />
        </button>
      </div>
    </div>
  );

  const renderStep4 = () => (
    <div className="wizard-step fade-in">
      <div className="step-header">
        <h2>Upload Your Photo</h2>
        <p className="step-subtitle">Take a photo of your door or window</p>
      </div>

      <div className="upload-container">
        <ImageUploader onImageSelect={handleImageSelect} />
      </div>

      <div className="wizard-actions">
        <button className="btn-back" onClick={prevStep}>
          <ArrowLeft size={18} /> Back
        </button>
        <button
          className="btn-next"
          onClick={nextStep}
          disabled={!formData.image}
        >
          Review <ArrowRight size={18} />
        </button>
      </div>
    </div>
  );

  const renderStep5 = () => (
    <div className="wizard-step fade-in">
      <div className="step-header">
        <h2>Ready to Visualize?</h2>
        <p className="step-subtitle">Review your selections</p>
      </div>

      <div className="review-card">
        <div className="review-item">
          <span className="label">Categories</span>
          <span className="value">{formData.categories.join(', ')}</span>
        </div>
        <div className="review-item">
          <span className="label">Mesh Type</span>
          <span className="value">{formData.meshChoice.replace('_', ' ')}</span>
        </div>
        <div className="review-item">
          <span className="label">Frame Color</span>
          <span className="value">
            <span className="color-dot" style={{
              backgroundColor: formData.frameColor === 'Dark Bronze' ? '#4B3621' :
                formData.frameColor === 'Stucco' ? '#9F9080' :
                  formData.frameColor === 'Almond' ? '#EADDcF' :
                    formData.frameColor.toLowerCase()
            }} />
            {formData.frameColor}
          </span>
        </div>
        <div className="review-item">
          <span className="label">Mesh Color</span>
          <span className="value">
            <span className="color-dot" style={{
              backgroundColor: formData.meshColor === 'Bronze' ? '#CD7F32' :
                formData.meshColor === 'Stucco' ? '#9F9080' :
                  'black'
            }} />
            {formData.meshColor}
          </span>
        </div>
        <div className="review-item">
          <span className="label">Image</span>
          <span className="value">{formData.image ? formData.image.name : 'None'}</span>
        </div>
      </div>

      {error && <div className="error-message">{error}</div>}

      <div className="wizard-actions">
        <button className="btn-back" onClick={prevStep}>
          <ArrowLeft size={18} /> Back
        </button>
        <button
          className="btn-submit"
          onClick={handleSubmit}
          disabled={isSubmitting}
        >
          {isSubmitting ? (
            <>Processing...</>
          ) : (
            <>Generate Visualization <Shield size={18} /></>
          )}
        </button>
      </div>
    </div>
  );

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

      {step === 1 && renderStep1()}
      {step === 2 && renderStep2()}
      {step === 3 && renderStep3()}
      {step === 4 && renderStep4()}
      {step === 5 && renderStep5()}
    </div>
  );
};

export default UploadPage;
