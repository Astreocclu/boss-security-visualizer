import React from 'react';
import { Link } from 'react-router-dom';

const ScreenTypesPage = ({ screenTypes }) => {
    return (
        <div className="screen-types-page" style={{ maxWidth: '1200px', margin: '0 auto', padding: '20px' }}>
            <div style={{ display: 'flex', alignItems: 'center', marginBottom: '20px' }}>
                <Link to="/" style={{ marginRight: '15px', textDecoration: 'none', fontSize: '24px', color: 'var(--white)' }}>←</Link>
                <h2>🖥️ Available Screen Types</h2>
            </div>
            <div style={{ display: 'grid', gap: '20px', marginTop: '20px' }}>
                {screenTypes.map(type => (
                    <div key={type.id} style={{
                        backgroundColor: 'var(--glass-bg)',
                        padding: '20px',
                        borderRadius: 'var(--radius-lg)',
                        border: '1px solid var(--glass-border)',
                        backdropFilter: 'blur(12px)'
                    }}>
                        <h3 style={{ color: 'var(--gold-primary)' }}>{type.name}</h3>
                        <p>{type.description || 'No description available'}</p>
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '10px', fontSize: '14px', color: 'var(--slate)' }}>
                            <span>Requests: {type.request_count || 0}</span>
                            <span>Status: {type.is_active ? '✅ Active' : '❌ Inactive'}</span>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default ScreenTypesPage;
