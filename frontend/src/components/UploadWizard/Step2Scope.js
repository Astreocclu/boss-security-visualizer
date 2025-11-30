import { useState } from 'react';
import { ArrowLeft, Home, Shield, DoorOpen } from 'lucide-react';
import useVisualizationStore from '../../store/visualizationStore';

const Step2Scope = ({ nextStep, prevStep }) => {
    const { setScope } = useVisualizationStore();
    const [subStep, setSubStep] = useState('patio');

    const handleYes = (key, value = true) => {
        setScope(key, value);
        // Pass the value directly for branching decisions
        advanceSubStep(key, true);
    };

    const handleNo = (key) => {
        setScope(key, false);
        if (key === 'hasDoors') {
            setScope('doorType', null);
        }
        // Pass the value directly for branching decisions
        advanceSubStep(key, false);
    };

    const advanceSubStep = (lastKey, lastValue) => {
        if (subStep === 'patio') {
            setSubStep('windows');
        } else if (subStep === 'windows') {
            setSubStep('doors');
        } else if (subStep === 'doors') {
            // Use the passed value instead of reading from scope
            if (lastKey === 'hasDoors' && lastValue === true) {
                setSubStep('doorType');
            } else {
                nextStep();
            }
        } else if (subStep === 'doorType') {
            nextStep();
        }
    };

    const selectDoorType = (type) => {
        setScope('doorType', type);
        nextStep();
    };

    return (
        <div className="wizard-step fade-in">
            {/* PATIO */}
            {subStep === 'patio' && (
                <>
                    <div className="step-header">
                        <Home size={48} className="step-icon" />
                        <h2>Do you have a covered patio or outdoor area?</h2>
                        <p className="step-subtitle">We can enclose it with security screens</p>
                    </div>
                    <div className="choice-cards">
                        <button className="choice-card yes" onClick={() => handleYes('hasPatio')}>
                            <Shield size={32} />
                            <span>Yes, enclose it</span>
                        </button>
                        <button className="choice-card no" onClick={() => handleNo('hasPatio')}>
                            <span>No thanks</span>
                        </button>
                    </div>
                </>
            )}

            {/* WINDOWS */}
            {subStep === 'windows' && (
                <>
                    <div className="step-header">
                        <Shield size={48} className="step-icon" />
                        <h2>Do you want security screens on your windows?</h2>
                        <p className="step-subtitle">Our screens mount over your windows, providing protection without blocking the view</p>
                    </div>
                    <div className="choice-cards">
                        <button className="choice-card yes" onClick={() => handleYes('hasWindows')}>
                            <Shield size={32} />
                            <span>Yes, secure them</span>
                        </button>
                        <button className="choice-card no" onClick={() => handleNo('hasWindows')}>
                            <span>No thanks</span>
                        </button>
                    </div>
                </>
            )}

            {/* DOORS */}
            {subStep === 'doors' && (
                <>
                    <div className="step-header">
                        <DoorOpen size={48} className="step-icon" />
                        <h2>Do you need security doors?</h2>
                        <p className="step-subtitle">Heavy-duty protection for your entryways</p>
                    </div>
                    <div className="choice-cards">
                        <button className="choice-card yes" onClick={() => handleYes('hasDoors')}>
                            <Shield size={32} />
                            <span>Yes, I need doors</span>
                        </button>
                        <button className="choice-card no" onClick={() => handleNo('hasDoors')}>
                            <span>No thanks</span>
                        </button>
                    </div>
                </>
            )}

            {/* DOOR TYPE */}
            {subStep === 'doorType' && (
                <>
                    <div className="step-header">
                        <DoorOpen size={48} className="step-icon" />
                        <h2>What type of door?</h2>
                        <p className="step-subtitle">Choose the style that fits your home</p>
                    </div>
                    <div className="choice-cards vertical">
                        <button className="choice-card" onClick={() => selectDoorType('security_door')}>
                            <span>Standard Security Door</span>
                        </button>
                        <button className="choice-card" onClick={() => selectDoorType('french_door')}>
                            <span>French Doors (Double)</span>
                        </button>
                        <button className="choice-card" onClick={() => selectDoorType('sliding_door')}>
                            <span>Sliding Door</span>
                        </button>
                    </div>
                </>
            )}

            <div className="wizard-actions">
                <button className="btn-back" onClick={prevStep}>
                    <ArrowLeft size={18} /> Back
                </button>
            </div>
        </div>
    );
};

export default Step2Scope;
