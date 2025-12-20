import React, { useState } from 'react';
import DynamicForm from '../components/DynamicForm';
import bossSchema from '../config/schemas/boss.schema.json';
import poolsSchema from '../config/schemas/pools.schema.json';
import './SchemaTestPage.css';

const schemas = {
    boss: bossSchema,
    pools: poolsSchema,
};

const SchemaTestPage = () => {
    const [activeSchema, setActiveSchema] = useState('boss');
    const [formData, setFormData] = useState({});

    const handleSchemaChange = (schemaKey) => {
        setActiveSchema(schemaKey);
        setFormData({}); // Reset form when switching schemas
    };

    const currentSchema = schemas[activeSchema];

    return (
        <div className="schema-test-page">
            <div className="schema-test-header">
                <h1>Dynamic Form Schema Test</h1>
                <p className="schema-test-subtitle">
                    Proves the frontend can render forms from JSON config without knowing the product domain
                </p>
            </div>

            <div className="schema-toggle">
                {Object.keys(schemas).map((key) => (
                    <button
                        key={key}
                        className={`toggle-btn ${activeSchema === key ? 'active' : ''}`}
                        onClick={() => handleSchemaChange(key)}
                    >
                        {schemas[key].display_name}
                    </button>
                ))}
            </div>

            <div className="schema-test-content">
                <div className="form-panel">
                    <DynamicForm
                        schema={currentSchema}
                        formData={formData}
                        onChange={setFormData}
                    />
                </div>

                <div className="state-panel">
                    <div className="state-header">
                        <h3>Current Form State</h3>
                        <span className="state-badge">Live JSON</span>
                    </div>
                    <pre className="state-json">
                        {JSON.stringify(
                            {
                                tenant_id: currentSchema.tenant_id,
                                selections: formData,
                            },
                            null,
                            2
                        )}
                    </pre>
                </div>
            </div>

            <div className="schema-test-footer">
                <div className="proof-box">
                    <strong>✓ Proof:</strong> Switching schemas changes visible fields with zero code changes.
                    Each schema defines its own product categories.
                </div>
            </div>
        </div>
    );
};

export default SchemaTestPage;
