import React from 'react';
import './DynamicForm.css';

/**
 * DynamicForm - Renders form fields from a JSON schema
 * Domain-agnostic: no hardcoded product references
 * 
 * @param {Object} schema - Schema with product_categories array
 * @param {Object} formData - Current form state
 * @param {Function} onChange - Callback with updated form state
 */
const DynamicForm = ({ schema, formData = {}, onChange }) => {
    if (!schema?.product_categories) {
        return <div className="dynamic-form-empty">No schema provided</div>;
    }

    const handleFieldChange = (key, value) => {
        const newFormData = {
            ...formData,
            [key]: value
        };
        onChange?.(newFormData);
    };

    const renderField = (category) => {
        const { key, label, type, required, options } = category;
        const value = formData[key] || '';

        switch (type) {
            case 'select':
                return (
                    <div className="form-field" key={key}>
                        <label htmlFor={key}>
                            {label}
                            {required && <span className="required">*</span>}
                        </label>
                        <select
                            id={key}
                            value={value}
                            onChange={(e) => handleFieldChange(key, e.target.value)}
                            required={required}
                        >
                            <option value="">Select {label}</option>
                            {options?.map((opt) => (
                                <option key={opt.value} value={opt.value}>
                                    {opt.label}
                                </option>
                            ))}
                        </select>
                    </div>
                );

            case 'text':
                return (
                    <div className="form-field" key={key}>
                        <label htmlFor={key}>
                            {label}
                            {required && <span className="required">*</span>}
                        </label>
                        <input
                            type="text"
                            id={key}
                            value={value}
                            onChange={(e) => handleFieldChange(key, e.target.value)}
                            required={required}
                        />
                    </div>
                );

            default:
                return (
                    <div className="form-field" key={key}>
                        <label>{label}: Unknown type "{type}"</label>
                    </div>
                );
        }
    };

    return (
        <div className="dynamic-form">
            <div className="dynamic-form-header">
                <h3>{schema.display_name || 'Form'}</h3>
                <span className="tenant-badge">{schema.tenant_id}</span>
            </div>
            <div className="dynamic-form-fields">
                {schema.product_categories.map(renderField)}
            </div>
        </div>
    );
};

export default DynamicForm;
