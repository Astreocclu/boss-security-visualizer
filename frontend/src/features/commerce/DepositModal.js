import React, { useState } from 'react';
import { X } from 'lucide-react';

// Note: In a real app, we would use @stripe/react-stripe-js here.
// For this prototype, we'll simulate the Stripe Elements flow.

const DepositModal = ({ isOpen, onClose, onConfirm }) => {
    const [processing, setProcessing] = useState(false);

    if (!isOpen) return null;

    const handlePayment = async () => {
        setProcessing(true);
        // Simulate API call delay
        setTimeout(() => {
            setProcessing(false);
            onConfirm();
        }, 2000);
    };

    return (
        <div className="modal-overlay" style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'rgba(0, 0, 0, 0.8)',
            backdropFilter: 'blur(5px)',
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            zIndex: 1000
        }}>
            <div className="modal-content" style={{
                background: 'var(--primary-navy)',
                border: '1px solid var(--gold-primary)',
                borderRadius: 'var(--radius-lg)',
                padding: '2rem',
                width: '90%',
                maxWidth: '500px',
                position: 'relative'
            }}>
                <button
                    onClick={onClose}
                    style={{
                        position: 'absolute',
                        top: '1rem',
                        right: '1rem',
                        background: 'none',
                        border: 'none',
                        color: 'var(--slate)',
                        padding: 0,
                        boxShadow: 'none'
                    }}
                >
                    <X size={24} />
                </button>

                <h2 style={{ textAlign: 'center', color: 'var(--white)', marginBottom: '2rem' }}>Secure Deposit</h2>

                {/* Mock Stripe Element */}
                <div className="stripe-mock" style={{ marginBottom: '2rem' }}>
                    <div style={{ marginBottom: '1rem' }}>
                        <label style={{ fontSize: '0.9rem', color: 'var(--slate)' }}>Card Information</label>
                        <div style={{
                            background: 'white',
                            padding: '12px',
                            borderRadius: '4px',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '10px'
                        }}>
                            <div style={{ width: '30px', height: '20px', background: '#ccc', borderRadius: '2px' }}></div>
                            <span style={{ color: '#333', fontFamily: 'monospace' }}>4242 4242 4242 4242</span>
                        </div>
                    </div>

                    <div style={{ display: 'flex', gap: '1rem' }}>
                        <div style={{ flex: 1 }}>
                            <label style={{ fontSize: '0.9rem', color: 'var(--slate)' }}>Expiration</label>
                            <div style={{ background: 'white', padding: '12px', borderRadius: '4px', color: '#333' }}>MM / YY</div>
                        </div>
                        <div style={{ flex: 1 }}>
                            <label style={{ fontSize: '0.9rem', color: 'var(--slate)' }}>CVC</label>
                            <div style={{ background: 'white', padding: '12px', borderRadius: '4px', color: '#333' }}>123</div>
                        </div>
                    </div>
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '2rem', color: 'var(--slate)', fontSize: '0.9rem' }}>
                    <span>Total Due</span>
                    <span style={{ color: 'var(--white)', fontWeight: 'bold' }}>$500.00</span>
                </div>

                <button
                    onClick={handlePayment}
                    disabled={processing}
                    style={{ width: '100%' }}
                >
                    {processing ? 'Processing...' : 'Pay $500.00'}
                </button>

                <p style={{ textAlign: 'center', marginTop: '1rem', fontSize: '0.8rem', color: 'var(--slate)' }}>
                    Payments processed securely by Stripe.
                </p>
            </div>
        </div>
    );
};

export default DepositModal;
