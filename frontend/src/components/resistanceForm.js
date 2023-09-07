import React, { useState } from 'react';
import { toast } from 'react-toastify';
import ResistanceInput from './resistanceInput';

function ResistanceForm() {
  const [resistances, setResistances] = useState([]);
  const [margins, setMargins] = useState([]);

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
    // Verifique se há 6 resistências e 6 margens definidas
    if (resistances.length !== 6 || margins.length !== 6) {
      toast.error('Por favor, defina 6 resistências e 6 margens antes de enviar os dados.', {
        position: toast.POSITION.TOP_CENTER,
        autoClose: 5000,
      });
      return; // Não continue se os dados não estiverem completos
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

  return (
    <div>
      {[1, 2, 3, 4, 5, 6].map((index) => (
        <ResistanceInput
          key={index}
          index={index}
          onResistanceChange={(value) => handleInputChange(index - 1, value, 'resistance')}
          onMarginChange={(value) => handleInputChange(index - 1, value, 'margin')}
        />
        
      ))}
      <button onClick={handleSubmit}>Submit</button>
    </div>
  );
}

export default ResistanceForm;
