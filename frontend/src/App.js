import React, { useState } from 'react';
import './App.css';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import ResistanceForm from './components/resistanceForm';
import ResistorComponent from './components/resistorComponent';

function App() {
  const [resistance, setResistance] = useState(0);

  const handleResistanceChange = (newResistance) => {
    setResistance(newResistance);
  };

  return (
    <div className="App">
      <div className="wizard-icon">🧙‍♂️</div>
      <h1 className="title">Resistor Wizard ⚡</h1>
      <ResistanceForm onResistanceChange={handleResistanceChange} />
      <ResistorComponent className="resistor-component" resistance={resistance} />
      <ToastContainer />
    </div>
  );
}

export default App;
