import React, { useState } from 'react';
import ResistorComponent from './resistorComponent';
import { toast } from 'react-toastify';

function ResistanceForm() {
  const [resistances, setResistances] = useState(Array(5).fill(''));
  const [margins, setMargins] = useState(Array(5).fill(''));
  const [currentIndex, setCurrentIndex] = useState(0);

  const findNearestResistance = (inputValue) => {
    const inputValueString = inputValue.toString().split('.')[0];
    const firstTwoDigitsAsString = inputValueString.substring(0, 2);
    const firstTwoDigits = parseInt(firstTwoDigitsAsString);
    const digitsToTheRight = inputValueString.substring(2).length;
    const result = firstTwoDigits * Math.pow(10, digitsToTheRight);
    return result;
  }

  const handleInputChange = (index, value, type) => {
    if (value.trim() === '') {
      if (type === 'resistance') {
        setResistances(prevResistances => {
          const updatedResistances = [...prevResistances];
          updatedResistances[index] = '';
          return updatedResistances;
        });
      } else if (type === 'margin') {
        setMargins(prevMargins => {
          const updatedMargins = [...prevMargins];
          updatedMargins[index] = '';
          return updatedMargins;
        });
      }
      return;
    }
  
    const numericValue = parseFloat(value);
  
    if (!isNaN(numericValue)) {
      if (type === 'resistance') {
        const nearestResistance = findNearestResistance(numericValue);
        setResistances(prevResistances => {
          const updatedResistances = [...prevResistances];
          updatedResistances[index] = nearestResistance;
          return updatedResistances;
        });
      } else if (type === 'margin') {
        setMargins(prevMargins => {
          const updatedMargins = [...prevMargins];
          updatedMargins[index] = numericValue;
          return updatedMargins;
        });
      }
    } else {
      handleInvalidInput();
    }
  };
  const handleNextInput = () => {
    if (currentIndex < 4) {
      setCurrentIndex(currentIndex + 1);
    } else {
      handleFormSubmission();    }
  };
  const handlePreviousInput = () => {
    if (currentIndex > 0) {
      setCurrentIndex(currentIndex - 1);
    }
  };
  const handleInvalidInput = () => {
    toast.error('Por favor, insira um valor numérico.', {
      position: toast.POSITION.TOP_CENTER,
      autoClose: 3000,
    });
  };

  const handleFormSubmission = async () => {
    if (resistances.length !== 5 || margins.length !== 5) {
      toast.error('Por favor, defina 5 resistências e 5 margens antes de enviar os dados.', {
        position: toast.POSITION.TOP_CENTER,
        autoClose: 5000,
      });
      return;
    }

    const dataToSend = [];
    for (let i = 0; i < 5; i++) {
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

  return (
    <div>
      <label htmlFor={`resistance${currentIndex}`}>Resistance {currentIndex + 1}</label>
      <input
        type="text"
        name={`resistance${currentIndex}`}
        value={resistances[currentIndex] || ''}
        onChange={e => handleInputChange(currentIndex, e.target.value, 'resistance')}
      />
  
      <label htmlFor={`margin${currentIndex}`}>Margin {currentIndex + 1}</label>
      <input
        type="text"
        name={`margin${currentIndex}`}
        value={margins[currentIndex] || ''}
        onChange={e => handleInputChange(currentIndex, e.target.value, 'margin')}
      />
    <div className="buttons">
      {currentIndex > 0 && (
        <button onClick={handlePreviousInput}>Previous</button>
      )}
      {currentIndex < 4 && (
        <button onClick={handleNextInput}>Next</button>
      )}
    </div>
      <ResistorComponent resistance={parseFloat(resistances[currentIndex])} />
    </div>
  );
}

export default ResistanceForm;
