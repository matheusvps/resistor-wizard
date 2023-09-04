import React from 'react';

function ResistanceInput({ index, onResistanceChange, onMarginChange }) {
  return (
    <div className="input-container">
      <label htmlFor={`resistance${index}`}>Resistance {index}</label>
      <input
        type="text"
        name={`resistance${index}`}
        onChange={(event) => onResistanceChange(event.target.value)}
      />
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
