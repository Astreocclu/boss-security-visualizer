import { Link, useLocation } from 'react-router-dom';
import { CheckCircle, Clock, FileText, ArrowLeft } from 'lucide-react';
import './QuoteSuccessPage.css';

const QuoteSuccessPage = () => {
  const location = useLocation();
  const visualizationId = location.state?.visualizationId;

  return (
    <div className="quote-success-page">
      <div className="quote-success-container">
        <div className="success-icon">
          <CheckCircle size={64} strokeWidth={1.5} />
        </div>

        <h1>Quote Generated Successfully</h1>

        <div className="quote-card">
          <div className="quote-row">
            <span className="quote-label">
              <FileText size={18} />
              Reference ID
            </span>
            <span className="quote-value">#BOSS-8821</span>
          </div>

          <div className="quote-row">
            <span className="quote-label">
              <CheckCircle size={18} />
              Status
            </span>
            <span className="quote-value status-sent">Sent to Monday.com CRM</span>
          </div>

          <div className="quote-row highlight">
            <span className="quote-label">Estimated Total</span>
            <span className="quote-value price">$2,400.00</span>
          </div>
        </div>

        <div className="next-steps">
          <div className="next-steps-icon">
            <Clock size={24} />
          </div>
          <h3>Next Step</h3>
          <p>
            A Boss Security representative will review this quote within 24 hours
            and contact you to schedule your installation consultation.
          </p>
        </div>

        <div className="quote-actions">
          {visualizationId && (
            <Link to={`/results/${visualizationId}`} className="btn btn-secondary">
              <ArrowLeft size={18} />
              Back to Visualization
            </Link>
          )}
          <Link to="/upload" className="btn btn-primary">
            Start New Visualization
          </Link>
        </div>
      </div>
    </div>
  );
};

export default QuoteSuccessPage;
