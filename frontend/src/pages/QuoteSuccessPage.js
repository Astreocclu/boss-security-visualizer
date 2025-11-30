import { Link, useLocation } from 'react-router-dom';
import { Mail, ArrowLeft, Shield, CheckCircle } from 'lucide-react';
import './QuoteSuccessPage.css';

const QuoteSuccessPage = () => {
  const location = useLocation();
  const { afterImageUrl } = location.state || {};

  const quoteDate = new Date().toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });

  const quoteNumber = `BOSS-${Math.floor(1000 + Math.random() * 9000)}`;

  return (
    <div className="quote-page">
      {/* Digital Paper Document */}
      <div className="quote-document">
        {/* Document Header */}
        <header className="doc-header">
          <div className="doc-header-left">
            <Shield className="doc-logo-icon" size={32} />
            <div className="doc-brand">
              <span className="doc-brand-name">BOSS</span>
              <span className="doc-brand-tagline">Security Screens</span>
            </div>
          </div>
          <div className="doc-header-right">
            <h1 className="doc-title">OFFICIAL QUOTATION</h1>
            <p className="doc-number">#{quoteNumber}</p>
          </div>
        </header>

        {/* Document Body */}
        <div className="doc-body">
          {/* Client & Quote Info Row */}
          <div className="doc-info-row">
            <div className="doc-info-block">
              <h3>Client Details</h3>
              <p className="client-name">John & Sarah Mitchell</p>
              <p className="client-address">
                4521 Willow Creek Drive<br />
                Dallas, TX 75201
              </p>
            </div>
            <div className="doc-info-block">
              <h3>Quote Information</h3>
              <p><strong>Date:</strong> {quoteDate}</p>
              <p><strong>Valid Until:</strong> 30 Days</p>
              <p><strong>Sales Rep:</strong> Marcus Johnson</p>
            </div>
          </div>

          {/* Visual Verification */}
          {afterImageUrl && (
            <div className="visual-verification">
              <h3>Visual Verification</h3>
              <div className="verification-image-wrapper">
                <img src={afterImageUrl} alt="Security Screen Preview" />
                <div className="verification-label">
                  <CheckCircle size={14} />
                  AI-Generated Preview
                </div>
              </div>
            </div>
          )}

          {/* Engineering Specs */}
          <div className="specs-section">
            <h3>Engineering Specifications</h3>
            <table className="specs-table">
              <tbody>
                <tr>
                  <td className="spec-label">Material</td>
                  <td className="spec-value">316 Marine Grade Stainless Steel Mesh (12x12)</td>
                </tr>
                <tr>
                  <td className="spec-label">Impact Rating</td>
                  <td className="spec-value">HVHZ Standards (100ft-lb)</td>
                </tr>
                <tr>
                  <td className="spec-label">Mounting</td>
                  <td className="spec-value">Tamper-proof concealed fasteners</td>
                </tr>
                <tr>
                  <td className="spec-label">Warranty</td>
                  <td className="spec-value">15-year comprehensive warranty</td>
                </tr>
              </tbody>
            </table>
          </div>

          {/* Itemized Costs */}
          <div className="costs-section">
            <h3>Itemized Investment</h3>
            <div className="cost-items">
              <div className="cost-line">
                <span className="cost-description">1x Security Screen Door (72" x 80")</span>
                <span className="cost-dots" />
                <span className="cost-amount">$2,500.00</span>
              </div>
              <div className="cost-line">
                <span className="cost-description">3x Security Screen Windows (36" x 48" ea.)</span>
                <span className="cost-dots" />
                <span className="cost-amount">$3,600.00</span>
              </div>
              <div className="cost-line sub-item">
                <span className="cost-description">Professional Installation</span>
                <span className="cost-dots" />
                <span className="cost-amount included">Included</span>
              </div>
            </div>

            <div className="cost-total">
              <span className="total-label">Total Investment</span>
              <span className="total-amount">$6,100.00</span>
            </div>
          </div>

          {/* Footer Note */}
          <div className="doc-footer-note">
            <p>
              This quote is valid for 30 days from the date of issue. Pricing includes
              professional measurement, fabrication, and installation by certified technicians.
              All products carry our comprehensive warranty and meet or exceed local building codes.
            </p>
          </div>
        </div>

        {/* Document Footer */}
        <footer className="doc-footer">
          <div className="footer-contact">
            <p>Boss Security Screens | Dallas-Fort Worth</p>
            <p>(972) 555-0123 | quotes@bosssecurityscreens.com</p>
          </div>
        </footer>
      </div>

      {/* Action Buttons (Outside the paper) */}
      <div className="quote-actions">
        <button className="btn-email-pdf">
          <Mail size={18} />
          EMAIL PDF TO CLIENT
        </button>
        <Link to="/" className="btn-return">
          <ArrowLeft size={18} />
          RETURN TO DASHBOARD
        </Link>
      </div>

      {/* CRM Sync Badge */}
      <div className="crm-badge">
        <span className="crm-dot" />
        Synced to CRM
      </div>
    </div>
  );
};

export default QuoteSuccessPage;
