/*
  This is the client side of the interaction between the arduino sensor array
  and the usb missile launcher. 
*/
#include <Arduino.h>

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
  delay(5000);
  Serial.flush();

  uint16_t reading;
  for (uint8_t i = 0; i < max_pins; i++) {
    reading = analogRead(i);
    default_voltages[i] = reading;

    if (reading) { // assumes non-occupied pins are grounded
      active_pins++;
    }
  }
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
    //Serial.print(default_voltages[i]); Serial.print(" ");
    // Serial.print(diff); Serial.print(" ");
    if (diff < 50) {
       Serial.print("Laser Tripped: ");
       Serial.println(i);
       delay(1000);
    }
  }
}

