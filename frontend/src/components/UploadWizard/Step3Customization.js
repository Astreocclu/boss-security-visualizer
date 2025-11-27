import React from 'react';
import { ArrowLeft, ArrowRight } from 'lucide-react';

const Step3Customization = ({ formData, setFormData, nextStep, prevStep }) => {
    const handleColorSelect = (type, color) => {
        setFormData(prev => ({ ...prev, [type]: color }));
    };

    return (
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
};

export default Step3Customization;
