
/*


  Teensy Tap

  A Teensy interface that is designed to
  - capture finger taps from a FSR
  - communicate tap timings to a PC through USB
  - deliver auditory feedback, possibly delayed, at every tap
  - play a metronome sound.


  Floris van Vugt, Sept 2017


 */




int fsrAnalogPin = 0; // FSR is connected to analog 0
int fsrReading;      // the analog reading from the FSR resistor divider

void setup(void) {
  Serial.begin(38400);   // We'll send debugging information via the Serial monitor
}

void loop(void) {
  fsrReading = analogRead(fsrAnalogPin);
  Serial.print("Analog reading = ");
  Serial.println(fsrReading);
    
  delay(250);
}
