import React from 'react';
import { ArrowLeft, ArrowRight, Award } from 'lucide-react';

import { useTenantConfig } from '../../hooks/useTenantConfig';

const Step3Customization = ({ formData, setFormData, nextStep, prevStep }) => {
    const { config, loading } = useTenantConfig();

    const handleColorSelect = (type, color) => {
        setFormData(prev => ({ ...prev, [type]: color }));
    };

    const handleMeshSelect = (mesh) => {
        setFormData(prev => ({ ...prev, meshChoice: mesh }));
    };

    if (loading) {
        return <div className="wizard-step fade-in"><div className="step-header"><h2>Loading options...</h2></div></div>;
    }

    const meshOptions = config?.choices?.mesh?.map(([value, label]) => ({
        id: value,
        label,
        desc: value === '12x12_american' ? 'Marine-grade stainless steel' : (value === '10x10' ? 'Maximum security' : 'Industry standard security mesh'),
        badge: value === '12x12_american' ? 'Best Value' : null
    })) || [];

    const frameColorOptions = config?.choices?.frame_color?.map(([value, label]) => {
        let hex = '#000000';
        let border = false;
        if (value === 'Dark Bronze') hex = '#4B3621';
        if (value === 'Stucco') hex = '#9F9080';
        if (value === 'White') { hex = '#FFFFFF'; border = true; }
        if (value === 'Almond') hex = '#EADDcF';
        return { id: value, hex, border };
    }) || [];

    const meshColorOptions = config?.choices?.mesh_color?.map(([value, label]) => {
        let hex = '#000000';
        if (value === 'Stucco') hex = '#9F9080';
        if (value === 'Bronze') hex = '#CD7F32';
        return { id: value, hex, recommended: value === 'Black' };
    }) || [];

    return (
        <div className="wizard-step fade-in">
            <div className="step-header">
                <h2>Customize Your Look</h2>
                <p className="step-subtitle">Match your home's aesthetic</p>
            </div>

            {/* Mesh Selection */}
            <div className="customization-section">
                <h3>Mesh Type</h3>
                <div className="mesh-options">
                    {meshOptions.map(mesh => (
                        <div
                            key={mesh.id}
                            className={`mesh-card ${formData.meshChoice === mesh.id ? 'selected' : ''}`}
                            onClick={() => handleMeshSelect(mesh.id)}
                        >
                            <div className="mesh-card-header">
                                <h4>{mesh.label}</h4>
                                {mesh.badge && (
                                    <span className="mesh-badge">
                                        <Award size={14} /> {mesh.badge}
                                    </span>
                                )}
                            </div>
                            <p className="mesh-desc">{mesh.desc}</p>
                        </div>
                    ))}
                </div>
            </div>

            <div className="customization-section">
                <h3>Frame Color</h3>
                <div className="color-swatches-grid">
                    {frameColorOptions.map(color => (
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
                    {meshColorOptions.map(color => (
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
