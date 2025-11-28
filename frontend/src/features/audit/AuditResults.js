import React from 'react';
import { AlertTriangle, ShieldAlert, Lock, EyeOff } from 'lucide-react';

const AuditResults = ({ auditReport }) => {
    if (!auditReport) return null;

    const risks = [];
    if (auditReport.has_ground_level_access) {
        risks.push({
            icon: <AlertTriangle className="w-6 h-6 text-red-500" />,
            title: "Ground Level Access",
            desc: "Windows within 6ft of ground are primary entry points."
        });
    }
    if (auditReport.has_concealment) {
        risks.push({
            icon: <EyeOff className="w-6 h-6 text-red-500" />,
            title: "Concealed Entry",
            desc: "Landscaping hides potential intruders from view."
        });
    }
    if (auditReport.has_glass_proximity) {
        risks.push({
            icon: <Lock className="w-6 h-6 text-orange-500" />,
            title: "Glass Proximity",
            desc: "Glass near locks allows for 'break and reach' entry."
        });
    }
    if (auditReport.has_hardware_weakness) {
        risks.push({
            icon: <ShieldAlert className="w-6 h-6 text-red-500" />,
            title: "Hardware Weakness",
            desc: "Standard fly screens offer zero security protection."
        });
    }

    return (
        <div className="audit-results-container" style={{ marginTop: '2rem' }}>
            <h3 style={{ color: 'var(--brand-red)', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <ShieldAlert /> Security Vulnerability Assessment
            </h3>

            <div className="audit-summary" style={{
                background: 'rgba(211, 47, 47, 0.1)',
                padding: '1rem',
                borderRadius: 'var(--radius-md)',
                borderLeft: '4px solid var(--brand-red)',
                marginBottom: '1.5rem'
            }}>
                <p style={{ margin: 0, fontStyle: 'italic' }}>"{auditReport.analysis_summary}"</p>
            </div>

            <div className="risks-grid" style={{ display: 'grid', gap: '1rem', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))' }}>
                {risks.map((risk, index) => (
                    <div key={index} className="risk-card" style={{
                        background: 'rgba(255, 255, 255, 0.05)',
                        padding: '1rem',
                        borderRadius: 'var(--radius-md)',
                        display: 'flex',
                        alignItems: 'start',
                        gap: '1rem'
                    }}>
                        {risk.icon}
                        <div>
                            <h4 style={{ margin: '0 0 0.5rem 0', color: 'var(--white)' }}>{risk.title}</h4>
                            <p style={{ margin: 0, fontSize: '0.9rem', color: 'var(--slate)' }}>{risk.desc}</p>
                        </div>
                    </div>
                ))}
            </div>

            {risks.length === 0 && (
                <div style={{ textAlign: 'center', padding: '2rem', color: 'var(--gold-primary)' }}>
                    <ShieldAlert className="w-12 h-12 mx-auto mb-2" />
                    <p>No high-risk vulnerabilities detected by AI.</p>
                </div>
            )}
        </div>
    );
};

export default AuditResults;
