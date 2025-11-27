import React, { useState, useEffect } from 'react';
import { getScreenTypes } from '../../services/api';

const ScreenSelector = ({ onSelect, selectedScreenTypeId }) => {
  const [screenTypes, setScreenTypes] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch screen types when component mounts
  useEffect(() => {
    const fetchScreenTypes = async () => {
      setIsLoading(true);
      // Hardcoded list to ensure dropdown is populated immediately
      // Hardcoded list of Mesh Types as requested by user
      const data = [
        { id: '10x10', name: '10x10 Heavy Duty', description: 'Maximum Privacy & Strength' },
        { id: '12x12', name: '12x12 Standard', description: 'Balanced Visibility & Security' },
        { id: '12x12_american', name: '12x12 American Standard', description: 'High-Tensile Weave' },
      ];

      setScreenTypes(data);
      setError(null);

      // If no screen type is selected and we have screen types, select the first one
      if (!selectedScreenTypeId && data.length > 0) {
        onSelect(data[0].id);
      }
      setIsLoading(false);
    };

    fetchScreenTypes();
  }, [onSelect, selectedScreenTypeId]);

  const handleChange = (e) => {
    const screenTypeId = e.target.value;
    onSelect(screenTypeId);
  };

  if (isLoading) {
    return <div>Loading screen types...</div>;
  }

  if (error) {
    return <div className="error-message">{error}</div>;
  }

  if (screenTypes.length === 0) {
    return <div>No screen types available. Please contact an administrator.</div>;
  }

  return (
    <div className="screen-selector">
      <label htmlFor="screen-type">Select Screen Type:</label>
      <select
        id="screen-type"
        value={selectedScreenTypeId || ''}
        onChange={handleChange}
      >
        {screenTypes.map((type) => (
          <option key={type.id} value={type.id}>
            {type.name}
          </option>
        ))}
      </select>

      {selectedScreenTypeId && (
        <div className="selected-screen-info">
          {screenTypes.find(type => type.id === selectedScreenTypeId)?.description && (
            <p className="screen-description">
              {screenTypes.find(type => type.id === selectedScreenTypeId)?.description}
            </p>
          )}
        </div>
      )}
    </div>
  );
};

export default ScreenSelector;
