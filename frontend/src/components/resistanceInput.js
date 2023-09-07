import React, { useState } from 'react';
import ResistorComponent from './resistorComponent';

function ResistanceInput({ index, onResistanceChange, onMarginChange }) {
  const [resistanceValue, setResistanceValue] = useState('');

  const handleResistanceChange = (value) => {
    setResistanceValue(value);
    onResistanceChange(value);
  };

  return (
    <div className="input-container">
      <label htmlFor={`resistance${index}`}>Resistance {index}</label>
      <input
        type="text"
        name={`resistance${index}`}
        value={resistanceValue}
        onChange={(event) => handleResistanceChange(event.target.value)}
      />

      <ResistorComponent resistance={parseFloat(resistanceValue)} />
      <label htmlFor={`margin${index}`}>Margin {index}</label>
      <input
        type="text"
        name={`margin${index}`}
        onChange={(event) => onMarginChange(event.target.value)}
      />
    </div>
  );
}

export default ResistanceInput;
