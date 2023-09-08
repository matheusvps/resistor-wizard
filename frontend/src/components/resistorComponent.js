import React from 'react';

function getColorCodes(resistance) {
  const bands = {
    0: 'black',
    1: 'saddlebrown',
    2: 'red',
    3: 'orange',
    4: 'yellow',
    5: 'green',
    6: 'blue',
    7: 'purple',
    8: 'gray',
    9: 'white',
  };

  const resistanceString = resistance.toString();
  const totalDigits = resistanceString.length;
  
  const digit1 = parseInt(resistanceString[0]);
  const digit2 = parseInt(resistanceString[1]);
  const multiplierExponent = totalDigits - 2;
  const tolerance = 'gold';

  const color1 = bands[digit1];
  const color2 = bands[digit2];
  const colorMultiplier = bands[multiplierExponent];
  const colorTolerance = tolerance;

  return [color1, color2, colorMultiplier, colorTolerance];
}
  
  

export default function ResistorComponent({ resistance }) {
  if(resistance){
    const colors = getColorCodes(resistance);

    return (
  <div className="resistor-container">
    <div className="resistor-bands-container">
      <span className="first-resistor-band" style={{ backgroundColor: colors[0] }}></span>
      <span className="second-resistor-band" style={{ backgroundColor: colors[1] }}></span>
      <span className="third-resistor-band" style={{ backgroundColor: colors[2] }}></span>
      <span className="tolerance-resistor-band" style={{ backgroundColor: colors[3] }}></span>
    </div>
  </div>
    );
  }
  return (
  <div className="resistor-container">
    <div className="resistor-bands-container">
      <span className="unique-resistor-band" style={{ backgroundColor: 'gold' }}/>
    </div>
  </div>
  )
}