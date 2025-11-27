import React from 'react';

const MeshSelector = ({ onSelect, selectedMeshType }) => {
    const meshTypes = [
        { id: '10x10', name: '10x10 Heavy Duty', description: 'Maximum Privacy & Strength' },
        { id: '12x12', name: '12x12 Standard', description: 'Balanced Visibility & Security' },
        { id: '12x12_american', name: '12x12 American Standard', description: 'High-Tensile Weave' },
    ];

    const handleChange = (e) => {
        onSelect(e.target.value);
    };

    return (
        <div className="screen-selector" style={{ border: '2px solid red', padding: '10px', marginTop: '20px' }}>
            <h3 style={{ color: 'red' }}>DEBUG: MESH SELECTOR IS HERE</h3>
            <label htmlFor="mesh-type">Select Mesh Specification:</label>
            <select
                id="mesh-type"
                value={selectedMeshType || '12x12'}
                onChange={handleChange}
            >
                {meshTypes.map((type) => (
                    <option key={type.id} value={type.id}>
                        {type.name}
                    </option>
                ))}
            </select>

            <div className="selected-screen-info">
                <p className="screen-description">
                    {meshTypes.find(t => t.id === (selectedMeshType || '12x12'))?.description}
                </p>
            </div>
        </div>
    );
};

export default MeshSelector;
