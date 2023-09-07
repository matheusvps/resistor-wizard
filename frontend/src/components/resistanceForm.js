import React, { useState } from 'react';
import { toast } from 'react-toastify';

function ResistanceForm({ onResistanceChange }) {
  const [resistances, setResistances] = useState([]);
  const [margins, setMargins] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);

  function findNearestResistance(inputValue) {
    const inputValueString = inputValue.toString().split('.')[0];
    const firstTwoDigitsAsString = inputValueString.substring(0, 2);
    const firstTwoDigits = parseInt(firstTwoDigitsAsString);
    const digitsToTheRight = inputValueString.substring(2).length;
    const result = firstTwoDigits * Math.pow(10, digitsToTheRight);
    return result;
  }

  const handleInputChange = (index, value, type) => {
    const numericValue = parseFloat(value);
  
    if (!isNaN(numericValue)) {
      if (type === 'resistance') {
        const nearestResistance = findNearestResistance(numericValue);
        setResistances((prevResistances) => {
          const updatedResistances = [...prevResistances];
          updatedResistances[index] = nearestResistance;
          return updatedResistances;
        });
        onResistanceChange(nearestResistance);
      } else if (type === 'margin') {
        setMargins((prevMargins) => {
          const updatedMargins = [...prevMargins];
          updatedMargins[index] = numericValue;
          return updatedMargins;
        });
      }
    } else {
      toast.error('Por favor, insira um valor numérico.', {
        position: toast.POSITION.TOP_CENTER,
        autoClose: 3000,
      });
    }
  };
  

  const handleSubmit = async () => {
    if (resistances.length !== 6 || margins.length !== 6) {
      toast.error('Por favor, defina 6 resistências e 6 margens antes de enviar os dados.', {
        position: toast.POSITION.TOP_CENTER,
        autoClose: 5000,
      });
      return;
    }

    const dataToSend = [];
    for (let i = 0; i < 6; i++) {
      dataToSend.push({
        resistance: resistances[i],
        margin: margins[i],
      });
    }

    try {
      const response = await fetch('/api/send_resistances', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(dataToSend),
      });

      if (response.ok) {
        toast.success('Resistances sent successfully', {
          position: toast.POSITION.TOP_CENTER,
          autoClose: 3000,
        });
      } else {
        toast.error('Error sending resistances', {
          position: toast.POSITION.TOP_CENTER,
          autoClose: 3000,
        });
      }
    } catch (error) {
      console.error('Error:', error);
      toast.error('An error occurred', {
        position: toast.POSITION.TOP_CENTER,
        autoClose: 3000,
      });
    }
  };

  const handleNextInput = () => {
    if (currentIndex < 5) {
      setCurrentIndex(currentIndex + 1);
    } else {
      handleSubmit();
    }
  };

  return (
    <div>
      <label htmlFor={`resistance${currentIndex}`}>Resistance {currentIndex + 1}</label>
      <input
        type="text"
        name={`resistance${currentIndex}`}
        value={resistances[currentIndex] || ''}
        onChange={(event) => handleInputChange(currentIndex, event.target.value, 'resistance')}
      />

      <label htmlFor={`margin${currentIndex}`}>Margin {currentIndex + 1}</label>
      <input
        type="text"
        name={`margin${currentIndex}`}
        value={margins[currentIndex] || ''}
        onChange={(event) => handleInputChange(currentIndex, event.target.value, 'margin')}
      />

      <button onClick={handleNextInput}>Next</button>
    </div>
  );
}

export default ResistanceForm;