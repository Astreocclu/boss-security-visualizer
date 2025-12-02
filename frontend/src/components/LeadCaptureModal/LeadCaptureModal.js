import { useState } from 'react';
import { X, Download, Loader2, CheckCircle } from 'lucide-react';
import { createLead } from '../../services/api';
import './LeadCaptureModal.css';

const US_STATES = [
  { code: 'AL', name: 'Alabama' }, { code: 'AK', name: 'Alaska' }, { code: 'AZ', name: 'Arizona' },
  { code: 'AR', name: 'Arkansas' }, { code: 'CA', name: 'California' }, { code: 'CO', name: 'Colorado' },
  { code: 'CT', name: 'Connecticut' }, { code: 'DE', name: 'Delaware' }, { code: 'FL', name: 'Florida' },
  { code: 'GA', name: 'Georgia' }, { code: 'HI', name: 'Hawaii' }, { code: 'ID', name: 'Idaho' },
  { code: 'IL', name: 'Illinois' }, { code: 'IN', name: 'Indiana' }, { code: 'IA', name: 'Iowa' },
  { code: 'KS', name: 'Kansas' }, { code: 'KY', name: 'Kentucky' }, { code: 'LA', name: 'Louisiana' },
  { code: 'ME', name: 'Maine' }, { code: 'MD', name: 'Maryland' }, { code: 'MA', name: 'Massachusetts' },
  { code: 'MI', name: 'Michigan' }, { code: 'MN', name: 'Minnesota' }, { code: 'MS', name: 'Mississippi' },
  { code: 'MO', name: 'Missouri' }, { code: 'MT', name: 'Montana' }, { code: 'NE', name: 'Nebraska' },
  { code: 'NV', name: 'Nevada' }, { code: 'NH', name: 'New Hampshire' }, { code: 'NJ', name: 'New Jersey' },
  { code: 'NM', name: 'New Mexico' }, { code: 'NY', name: 'New York' }, { code: 'NC', name: 'North Carolina' },
  { code: 'ND', name: 'North Dakota' }, { code: 'OH', name: 'Ohio' }, { code: 'OK', name: 'Oklahoma' },
  { code: 'OR', name: 'Oregon' }, { code: 'PA', name: 'Pennsylvania' }, { code: 'RI', name: 'Rhode Island' },
  { code: 'SC', name: 'South Carolina' }, { code: 'SD', name: 'South Dakota' }, { code: 'TN', name: 'Tennessee' },
  { code: 'TX', name: 'Texas' }, { code: 'UT', name: 'Utah' }, { code: 'VT', name: 'Vermont' },
  { code: 'VA', name: 'Virginia' }, { code: 'WA', name: 'Washington' }, { code: 'WV', name: 'West Virginia' },
  { code: 'WI', name: 'Wisconsin' }, { code: 'WY', name: 'Wyoming' }, { code: 'DC', name: 'District of Columbia' },
];

const LeadCaptureModal = ({ isOpen, onClose, visualizationId, isSalesRep = false }) => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    address_street: '',
    address_city: '',
    address_state: '',
    address_zip: '',
    is_existing_customer: false,
  });
  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);

  if (!isOpen) return null;

  const validateForm = () => {
    const newErrors = {};

    if (!formData.name.trim()) newErrors.name = 'Name is required';
    if (!formData.email.trim()) {
      newErrors.email = 'Email is required';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Invalid email format';
    }
    if (!formData.phone.trim()) {
      newErrors.phone = 'Phone is required';
    } else if (formData.phone.replace(/\D/g, '').length < 10) {
      newErrors.phone = 'Phone must be at least 10 digits';
    }
    if (!formData.address_street.trim()) newErrors.address_street = 'Street address is required';
    if (!formData.address_city.trim()) newErrors.address_city = 'City is required';
    if (!formData.address_state) newErrors.address_state = 'State is required';
    if (!formData.address_zip.trim()) {
      newErrors.address_zip = 'ZIP code is required';
    } else if (formData.address_zip.replace(/\D/g, '').length < 5) {
      newErrors.address_zip = 'ZIP must be at least 5 digits';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: null }));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validateForm()) return;

    setIsSubmitting(true);
    try {
      const response = await createLead({
        visualization_id: visualizationId,
        ...formData
      });

      // Trigger PDF download
      if (response.pdf_url) {
        window.open(response.pdf_url, '_blank');
      }

      setIsSuccess(true);
      setTimeout(() => {
        onClose();
        setIsSuccess(false);
        setFormData({
          name: '', email: '', phone: '',
          address_street: '', address_city: '', address_state: '', address_zip: '',
          is_existing_customer: false,
        });
      }, 2000);

    } catch (err) {
      console.error('Lead submission error:', err);
      setErrors({ submit: err.message || 'Failed to submit. Please try again.' });
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isSuccess) {
    return (
      <div className="modal-overlay" onClick={onClose}>
        <div className="modal-content success-content" onClick={e => e.stopPropagation()}>
          <CheckCircle size={64} className="success-icon" />
          <h2>Download Started!</h2>
          <p>Your security report is downloading.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content lead-capture-modal" onClick={e => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose}>
          <X size={24} />
        </button>

        <div className="modal-header">
          <Download size={32} className="modal-icon" />
          <h2>Get Your Free Security Report</h2>
          <p>Enter your details to download your personalized security assessment.</p>
        </div>

        <form onSubmit={handleSubmit} className="lead-form">
          {errors.submit && <div className="form-error global">{errors.submit}</div>}

          <div className="form-group">
            <label htmlFor="name">Full Name *</label>
            <input
              type="text"
              id="name"
              name="name"
              value={formData.name}
              onChange={handleChange}
              placeholder="John Smith"
              className={errors.name ? 'error' : ''}
            />
            {errors.name && <span className="field-error">{errors.name}</span>}
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="email">Email *</label>
              <input
                type="email"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                placeholder="john@example.com"
                className={errors.email ? 'error' : ''}
              />
              {errors.email && <span className="field-error">{errors.email}</span>}
            </div>

            <div className="form-group">
              <label htmlFor="phone">Phone *</label>
              <input
                type="tel"
                id="phone"
                name="phone"
                value={formData.phone}
                onChange={handleChange}
                placeholder="(555) 123-4567"
                className={errors.phone ? 'error' : ''}
              />
              {errors.phone && <span className="field-error">{errors.phone}</span>}
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="address_street">Street Address *</label>
            <input
              type="text"
              id="address_street"
              name="address_street"
              value={formData.address_street}
              onChange={handleChange}
              placeholder="123 Main Street"
              className={errors.address_street ? 'error' : ''}
            />
            {errors.address_street && <span className="field-error">{errors.address_street}</span>}
          </div>

          <div className="form-row three-col">
            <div className="form-group">
              <label htmlFor="address_city">City *</label>
              <input
                type="text"
                id="address_city"
                name="address_city"
                value={formData.address_city}
                onChange={handleChange}
                placeholder="Phoenix"
                className={errors.address_city ? 'error' : ''}
              />
              {errors.address_city && <span className="field-error">{errors.address_city}</span>}
            </div>

            <div className="form-group">
              <label htmlFor="address_state">State *</label>
              <select
                id="address_state"
                name="address_state"
                value={formData.address_state}
                onChange={handleChange}
                className={errors.address_state ? 'error' : ''}
              >
                <option value="">Select...</option>
                {US_STATES.map(state => (
                  <option key={state.code} value={state.code}>{state.name}</option>
                ))}
              </select>
              {errors.address_state && <span className="field-error">{errors.address_state}</span>}
            </div>

            <div className="form-group">
              <label htmlFor="address_zip">ZIP *</label>
              <input
                type="text"
                id="address_zip"
                name="address_zip"
                value={formData.address_zip}
                onChange={handleChange}
                placeholder="85001"
                className={errors.address_zip ? 'error' : ''}
              />
              {errors.address_zip && <span className="field-error">{errors.address_zip}</span>}
            </div>
          </div>

          {isSalesRep && (
            <div className="form-group checkbox-group">
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  name="is_existing_customer"
                  checked={formData.is_existing_customer}
                  onChange={handleChange}
                />
                <span>Existing customer in CRM</span>
              </label>
            </div>
          )}

          <button type="submit" className="btn-submit" disabled={isSubmitting}>
            {isSubmitting ? (
              <>
                <Loader2 size={20} className="spinner" />
                Processing...
              </>
            ) : (
              <>
                <Download size={20} />
                Download Security Report
              </>
            )}
          </button>
        </form>
      </div>
    </div>
  );
};

export default LeadCaptureModal;
