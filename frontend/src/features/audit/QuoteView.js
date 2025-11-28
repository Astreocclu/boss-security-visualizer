import React from 'react';
import { Download, CreditCard, CheckCircle } from 'lucide-react';

const QuoteView = ({ visualizationRequest, onBuyNow, onDownloadPdf }) => {
    // Mock pricing logic based on scope
    const calculateTotal = () => {
        let total = 0;
        const scope = visualizationRequest.scope || {};
        if (scope.hasWindows) total += 1350;
        if (scope.hasDoors) total += 1200;
        if (scope.hasPatio) total += 2500;
        return total > 0 ? total : 1500; // Default fallback
    };

    const total = calculateTotal();
    const deposit = 500;

    return (
        <div className="quote-view-container" style={{ marginTop: '3rem' }}>
            <h2 style={{ textAlign: 'center', marginBottom: '2rem' }}>Your Investment</h2>

            <div className="quote-card" style={{
                background: 'var(--light-navy)',
                padding: '2rem',
                borderRadius: 'var(--radius-lg)',
                border: '1px solid var(--gold-muted)',
                maxWidth: '600px',
                margin: '0 auto'
            }}>
                <div className="quote-header" style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1.5rem', borderBottom: '1px solid var(--glass-border)', paddingBottom: '1rem' }}>
                    <span>Estimated Total</span>
                    <span style={{ fontSize: '1.5rem', fontWeight: 'bold', color: 'var(--white)' }}>${total.toLocaleString()}</span>
                </div>

                <div className="quote-items" style={{ marginBottom: '2rem' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem', color: 'var(--slate)' }}>
                        <span>Security Assessment</span>
                        <span style={{ color: 'var(--gold-primary)' }}>INCLUDED</span>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem', color: 'var(--slate)' }}>
                        <span>Installation</span>
                        <span>TBD</span>
                    </div>
                </div>

                <div className="deposit-section" style={{
                    background: 'rgba(212, 175, 55, 0.1)',
                    padding: '1.5rem',
                    borderRadius: 'var(--radius-md)',
                    textAlign: 'center',
                    marginBottom: '2rem'
                }}>
                    <h3 style={{ color: 'var(--gold-primary)', margin: '0 0 0.5rem 0' }}>Lock in Pricing</h3>
                    <p style={{ margin: '0 0 1rem 0', fontSize: '0.9rem' }}>Fully refundable $500 deposit to schedule your precision measurement.</p>
                    <button
                        onClick={onBuyNow}
                        style={{ width: '100%', display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '0.5rem' }}
                    >
                        <CreditCard size={20} /> Place ${deposit} Deposit
                    </button>
                </div>

                <div className="actions" style={{ display: 'flex', justifyContent: 'center' }}>
                    <button
                        onClick={onDownloadPdf}
                        className="btn-secondary"
                        style={{
                            background: 'transparent',
                            border: '1px solid var(--slate)',
                            color: 'var(--slate)',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '0.5rem'
                        }}
                    >
                        <Download size={18} /> Download Official Quote (PDF)
                    </button>
                </div>

                <div className="guarantee" style={{ marginTop: '2rem', textAlign: 'center', fontSize: '0.8rem', color: 'var(--slate)' }}>
                    <CheckCircle size={16} style={{ display: 'inline', marginRight: '4px', verticalAlign: 'text-bottom' }} />
                    Backed by the Boss "No Break-In" Guarantee
                </div>
            </div>
        </div>
    );
};

export default QuoteView;
