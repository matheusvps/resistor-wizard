import React, { useState } from 'react';
import './App.css';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import ResistanceForm from './components/resistanceForm';

function App() {
  const [setResistance] = useState(0);

  const handleResistanceChange = (newResistance) => {
    setResistance(newResistance);
  };

  return (
    <div className="App">
      <h1 className="title">
        <img src="/logo.png" alt="Logo" className='logo'/>      
        </h1>
      <ResistanceForm onResistanceChange={handleResistanceChange} />
      <ToastContainer />
    </div>
  );
}

export default App;
