import React from 'react';
import './App.css';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import ResistanceForm from './components/resistanceForm';

function App() {
  return (
    <div className="App">
      <div className="wizard-icon">🧙‍♂️</div>
      <h1 className="title">Resistor Wizard ⚡</h1>
      <ResistanceForm />
      <ToastContainer />
    </div>
  );
}

export default App;
