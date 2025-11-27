import React from 'react';
import { ArrowLeft, Shield } from 'lucide-react';

const Step5Review = ({ formData, prevStep, handleSubmit, isSubmitting, error }) => {
    return (
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
};

export default Step5Review;
