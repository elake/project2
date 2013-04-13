/*
  This is the client side of the interaction between the arduino sensor array
  and the usb missile launcher. 
*/
#include <Arduino.h>

// we set this to 10 because grounding so many pins consumes a lot of space on the
// breadboard, but theoretically you could have as many sensors as you want in your
// array
const uint8_t max_pins = 10; 

uint16_t default_voltages[max_pins];
uint8_t active_pins = 0;

void setup()
{
  /*
    setting up the client:
    1) determine out of 15 pins which ones have sensors plugged in
    2) send this number to the server
  */
  Serial.begin(9600);
  Serial.flush();
  delay(5000); // double flush the serial monitor
  Serial.flush();

  uint16_t reading; // mark which pins are currently active on the board
  for (uint8_t i = 0; i < max_pins; i++) { 
    reading = analogRead(i);
    default_voltages[i] = reading;
    if (reading) { // assumes non-occupied pins are grounded
      Serial.println(reading);
      active_pins++;
    }
  }
  // send this information to the serial port, where the server is waiting for it
  Serial.print("Number of pins active: ");
  Serial.println(active_pins); 
}

void loop()
{
  // loop: send to the server which sensors are interrupted
  int reading;
  int diff;
  for (uint8_t i = 0; i < active_pins; i++) {
    reading = analogRead(i);
    // Serial.print(reading); Serial.print(" ");
    diff = default_voltages[i] - reading;
    if (diff < -100) { 
      // detect voltage drops increases; this reduces misfires attributable to
      // ambient lighting changes
      Serial.print("Laser Tripped: "); // send the interrupted sensor to the server
      Serial.println(i);
      delay(1500); // delaying client side is the simplest solution
    }
  }
}

