import React from 'react';

function getColorCodes(resistance) {
  const bands = {
    0: 'black',
    1: 'brown',
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
  const colors = getColorCodes(resistance);

  const color1Class = `resistor-band ${colors[0]}`;
  const color2Class = `resistor-band ${colors[1]}`;
  const colorMultiplierClass = `resistor-band ${colors[2]}`;

  return (
      <div className="resistor-bands-container">
        <div className={color1Class} style={{ backgroundColor: colors[0] }}></div>
        <div className={color2Class} style={{ backgroundColor: colors[1] }}></div>
        <div className={colorMultiplierClass} style={{ backgroundColor: colors[2] }}></div>
        <img src="/resistor-without-background.png" alt="Resistor" className="resistor-image" />      
      </div>
  );
}