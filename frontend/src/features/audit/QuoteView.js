import { Download } from 'lucide-react';

const QuoteView = ({ onDownloadPdf }) => {
    return (
        <div className="download-report-container" style={{
            marginTop: '2rem',
            display: 'flex',
            justifyContent: 'center'
        }}>
            <button
                onClick={onDownloadPdf}
                style={{
                    background: 'var(--gold-primary)',
                    color: 'var(--deep-navy)',
                    border: 'none',
                    padding: '1rem 2rem',
                    borderRadius: 'var(--radius-md)',
                    fontSize: '1rem',
                    fontWeight: 'bold',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem',
                    cursor: 'pointer'
                }}
            >
                <Download size={20} /> Download Security Report
            </button>
        </div>
    );
};

export default QuoteView;
