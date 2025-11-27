import React from 'react';
import { DoorOpen, Maximize, LayoutTemplate, Check, ArrowRight } from 'lucide-react';

const Step1Categories = ({ formData, setFormData, nextStep }) => {
    const handleCategoryToggle = (category) => {
        setFormData(prev => {
            const newCategories = prev.categories.includes(category)
                ? prev.categories.filter(c => c !== category)
                : [...prev.categories, category];
            return { ...prev, categories: newCategories };
        });
    };

    return (
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
};

export default Step1Categories;
