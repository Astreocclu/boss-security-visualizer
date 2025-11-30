import React from 'react';
import { Shield, Star, ArrowLeft, ArrowRight } from 'lucide-react';

import { useTenantConfig } from '../../hooks/useTenantConfig';

const Step2Mesh = ({ formData, setFormData, nextStep, prevStep }) => {
    const { config, loading } = useTenantConfig();

    const handleMeshSelect = (mesh) => {
        setFormData(prev => ({ ...prev, meshChoice: mesh }));
    };

    if (loading) {
        return <div className="wizard-step fade-in"><div className="step-header"><h2>Loading options...</h2></div></div>;
    }

    const meshOptions = config?.choices?.mesh?.map(([value, label]) => {
        // Map visual properties based on ID (could be moved to config in future)
        const isPremium = value === '12x12_american';
        return {
            id: value,
            label: label,
            desc: isPremium ? 'Premium Marine Grade' : (value === '10x10' ? 'Heavy Duty Protection' : 'Enhanced Security Mesh'),
            icon: isPremium ? Star : Shield,
            badge: isPremium ? 'Best Value' : null
        };
    }) || [];

    return (
        <div className="wizard-step fade-in">
            <div className="step-header">
                <h2>Select Protection Level</h2>
                <p className="step-subtitle">Choose the mesh strength for your screens</p>
            </div>

            <div className="radio-card-grid">
                {meshOptions.map(mesh => {
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
};

export default Step2Mesh;
