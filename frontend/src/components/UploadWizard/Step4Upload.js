import React, { useCallback } from 'react';
import { ArrowLeft, ArrowRight } from 'lucide-react';
import ImageUploader from '../Upload/ImageUploader';

const Step4Upload = ({ formData, setFormData, nextStep, prevStep }) => {
    const handleImageSelect = useCallback((file) => {
        setFormData(prev => ({ ...prev, image: file }));
    }, [setFormData]);

    return (
        <div className="wizard-step fade-in">
            <div className="step-header">
                <h2>Upload Your Photo</h2>
                <p className="step-subtitle">Take a photo of your door or window</p>
            </div>

            <div className="upload-container">
                <ImageUploader
                    onImageSelect={handleImageSelect}
                    value={formData.image}
                />
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
};

export default Step4Upload;
