import React, { useState, useEffect } from 'react';
import { getScreenTypes } from '../../services/api';

const ScreenSelector = ({ onSelect, selectedScreenTypeId }) => {
  const [screenTypes, setScreenTypes] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch screen types when component mounts
  useEffect(() => {
    const fetchScreenTypes = async () => {
      try {
        setIsLoading(true);
        const response = await getScreenTypes();
        // Handle paginated response (DRF returns { results: [...] }) or flat array
        const data = response.results || response;
        setScreenTypes(data);
        setError(null);

        // If no screen type is selected and we have screen types, select the first one
        if (!selectedScreenTypeId && data.length > 0) {
          onSelect(data[0].id);
        }
      } catch (err) {
        console.error('Error fetching screen types:', err);
        setError('Failed to load screen types. Please try again later.');
      } finally {
        setIsLoading(false);
      }
    };

    fetchScreenTypes();
  }, [onSelect, selectedScreenTypeId]);

  const handleChange = (e) => {
    const screenTypeId = parseInt(e.target.value, 10);
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
