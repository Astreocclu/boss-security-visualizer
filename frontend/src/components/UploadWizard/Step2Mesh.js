import React from 'react';
import { Shield, Star, ArrowLeft, ArrowRight } from 'lucide-react';

const Step2Mesh = ({ formData, setFormData, nextStep, prevStep }) => {
    const handleMeshSelect = (mesh) => {
        setFormData(prev => ({ ...prev, meshChoice: mesh }));
    };

    return (
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
};

export default Step2Mesh;
