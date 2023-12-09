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

  const handleShutdown = async () => {
    try {
      const response = await fetch(`http://resistorwizard.local:5000/api/shutdown`, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        console.log('Shutdown successful');
      } else {
        console.error('Error shutting down');
      }
    } catch (error) {
      console.error('Error:', error);
    }
  };

  return (
    <div className="App">
      <div className="shutdown-button" onClick={handleShutdown}>
        <img src="/turnoff.png" alt="Shutdown" className='shutdown-icon' style={{ maxWidth: '50px', maxHeight: '50px' }}/>
      </div>
      <h1 className="title">
        <img src="/logo.png" alt="Logo" className='logo'/>      
      </h1>
      <ResistanceForm onResistanceChange={handleResistanceChange} />
      <ToastContainer />
    </div>
  );
}

export default App;