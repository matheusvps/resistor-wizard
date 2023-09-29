/* Sweep
 by BARRAGAN <http://barraganstudio.com>
 This example code is in the public domain.

 modified 8 Nov 2013
 by Scott Fitzgerald
 https://www.arduino.cc/en/Tutorial/LibraryExamples/Sweep
*/

#include <Servo.h>

Servo servo_baixo;  // create servo object to control a servo
Servo servo_cima;  // create servo object to control a servo
// twelve servo objects can be created on most boards

int d = 2000;
void setup() {
  servo_baixo.attach(9);  // attaches the servo on pin 9 to the servo object
  servo_cima.attach(10);  // attaches the servo on pin 9 to the servo object
}

void loop() {
  servo_baixo.write(0); // Baixo FECHA
  servo_cima.write(150); // Cima ABRE
  delay(d);
  servo_baixo.write(0); // Baixo FECHA
  servo_cima.write(180); // Cima FECHA
  delay(d);
  servo_baixo.write(30); // Baixo ABRE
  servo_cima.write(180); // Cima FECHA
  delay(d);
  servo_baixo.write(0); // Baixo FECHA
  servo_cima.write(180); // Cima FECHA
  delay(d);
}
