import React, { useState } from 'react';
import ResistorComponent from './resistorComponent';
import { toast } from 'react-toastify';
import ClipLoader from "react-spinners/ClipLoader";

function ResistanceForm() {
  const [resistances, setResistances] = useState(Array(5).fill(''));
  const [margins, setMargins] = useState(Array(5).fill(''));
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isRunning, setIsRunning] = useState(false);

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
    
    if (!isNaN(value)) {
      if (type === 'resistance') {
        const nearestResistance = findNearestResistance(value);
        setResistances(prevResistances => {
          const updatedResistances = [...prevResistances];
          updatedResistances[index] = nearestResistance;
          return updatedResistances;
        });
      } else if (type === 'margin') {
        setMargins(prevMargins => {
          const updatedMargins = [...prevMargins];
          updatedMargins[index] = value;
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
    setIsRunning(true);

    if (resistances.every(resistance => resistance === '') || margins.every(margin => margin === '')) {
      toast.error('Por favor, insira pelo menos uma resistência e uma margem antes de enviar os dados.', {
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
      const response = await fetch(`http://resistorwizard.local:5000/api/send_resistances`, {
        method: 'POST',
        credentials:'include',
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

  const handleStopButtonClick = async () => {
    try {
      const response = await fetch(`http://resistorwizard.local:5000/api/stop`, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        toast.success('Processo interrompido com sucesso', {
          position: toast.POSITION.TOP_CENTER,
          autoClose: 3000,
        });
        setIsRunning(false);
      } else {
        toast.error('Erro ao interromper o processo', {
          position: toast.POSITION.TOP_CENTER,
          autoClose: 3000,
        });
      }
    } catch (error) {
      console.error('Erro:', error);
      toast.error('Ocorreu um erro ao interromper o processo', {
        position: toast.POSITION.TOP_CENTER,
        autoClose: 3000,
      });
    }
  };

  return (
    <div>
      {isRunning ? (
        <div
          className="loading-container"
        >
          <span
            className="loading-title"
          >
          Em Andamento 
          </span>
          <ClipLoader
            color="rgba(0, 224, 255, 1)"
            speedMultiplier={0.4}
          />
        </div>
      ) : (
        <div>
          <label htmlFor={`resistance${currentIndex}`}>Resistance {currentIndex + 1}</label>
          <input
            type="number"
            step="any"
            name={`resistance${currentIndex}`}
            value={resistances[currentIndex] || ''}
            onChange={e => handleInputChange(currentIndex, e.target.value, 'resistance')}
          />
  
          <label htmlFor={`margin${currentIndex}`}>Margin {currentIndex + 1}</label>
          <input
            type="number"
            step="any"
            name={`margin${currentIndex}`}
            value={margins[currentIndex] || ''}
            onChange={e => handleInputChange(currentIndex, e.target.value, 'margin')}
          />
  
          <div className="buttons">
            {currentIndex > 0 && (
              <button onClick={handlePreviousInput} className="button">Previous</button>
            )}
            <button onClick={handleNextInput} className="button">Next</button>
            <button onClick={handleFormSubmission}>Submit</button>
          </div>
        </div>
      )}
      <ResistorComponent resistance={parseFloat(resistances[currentIndex])} />
      <div>
        {isRunning && (
          <button onClick={handleStopButtonClick} className="stop-button">Parar</button>
        )}
      </div>
    </div>
  );
}

export default ResistanceForm;
