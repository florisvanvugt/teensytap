/* FSR testing sketch. 
   
   Connect one end of FSR to 5V, the other end to Analog 0.
   Then connect one end of a 10K resistor from Analog 0 to ground
   Connect LED from pin 11 through a resistor to ground 
   
   For more information see www.ladyada.net/learn/sensors/fsr.html */

int fsrAnalogPin = 3; // the pin the FSR is connected to
int fsrReading;      // the analog reading from the FSR resistor divider

void setup(void) {
  Serial.begin(38400);   // We'll send debugging information via the Serial monitor
}

void loop(void) {
  fsrReading = analogRead(fsrAnalogPin);
  //Serial.print("Analog reading = ");
  Serial.print(fsrReading);
  Serial.print("\n");
    
  delay(50);
}
