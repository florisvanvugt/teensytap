
/*


  Teensy Tap

  A Teensy 3.2 interface that is designed to
  - capture finger taps from a FSR
  - communicate tap timings to a PC through USB
  - deliver auditory feedback, possibly delayed, at every tap
  - play a metronome sound.


  Floris van Vugt, Sept 2017
  Based on TapArduino


  This is code designed to work with Teensyduino
  (i.e. the Arduino IDE software used to generate code you can run on Teensy)

 */



int fsrAnalogPin = 0; // FSR is connected to analog 0
int fsrReading;      // the analog reading from the FSR resistor divider

// For interpreting taps
int tap_onset_threshold    = 20; // the FSR reading threshold necessary to flag a tap onset
int tap_offset_threshold   = 10; // the FSR reading threshold necessary to flag a tap offset
int min_tap_on_duration    = 20; // the minimum duration of a tap (in ms), this prevents double taps
int min_tap_off_duration   = 40; // the minimum time between offset of one tap and the onset of the next taps, again this prevents double taps


int tap_phase = 0; // The current tap phase, 0 = tap off (i.e. we are in the inter-tap-interval), 1 = tap on (we are within a tap)


unsigned long current_t            = 0; // the current time (in ms)
unsigned long prev_t               = 0; // the time stamp at the previous iteration (used to ensure correct loop time)
unsigned long next_event_embargo_t = 0; // the time when the next event is allowed to happen


unsigned long tap_onset_t = 0;  // the onset time of the current tap
unsigned long tap_offset_t = 0; // the offset time of the current tap
int           tap_max_force = 0; // the maximum force reading during the current tap
unsigned long tap_max_force_t = 0; // the time at which the maximum tap force was experienced

int tap_number = 0; // keep track of how many taps we have sent (to be able to later find whether some got lost along the way)


long baudrate = 9600; // the serial communication baudrate; not sure whether this actually does anything because Teensy documentation suggests that USB communication is always the highest possible.


int missed_frames = 0; // ideally our script should read the FSR every millisecond. we use this variable to check whether it may have skipped a millisecond





void setup(void) {
  /* This function will be executed once when we power up the Teensy */
  
  Serial.begin(baudrate);  // Initiate serial communication
  Serial.println("TeensyTap starting...");

}






void loop(void) {
  /* This is the main loop function which will be executed ad infinitum */

  current_t = millis(); // get current time (in ms)
  if (prev_t == 0) { prev_t = current_t; } // To prevent seeming "lost frames"

  if (current_t > prev_t) {
    // Main loop tick (one ms has passed)


    if (current_t-prev_t > 1) {
      // We missed a frame (or more)
      missed_frames += (current_t-prev_t);
    }
    

    /*
     * Collect data
     */
    fsrReading = analogRead(fsrAnalogPin);

    
    

    /*
     * Process data: has a new tap onset or tap offset occurred?
     */

    if (tap_phase==0) {
      // Currently we are in the tap-off phase (nothing was thouching the FSR)
      
      // First, check whether actually anything is allowed to happen.
      // For example, if a tap just happened then we don't allow another event,
      // for example we don't want taps to occur impossibly close (e.g. within a few milliseconds
      // we can't realistically have a tap onset and offset).
      // Second, check whether this a new tap onset
      if ( (current_t > next_event_embargo_t) && (fsrReading>tap_onset_threshold)) {

	// New Tap Onset
	tap_phase = 1; // currently we are in the tap "ON" phase
	tap_number += 1; // new tap!
	tap_onset_t = current_t;
	// don't allow an offset immediately; freeze the phase for a little while
	next_event_embargo_t = current_t + min_tap_on_duration; 
      }
      
    } else if (tap_phase==1) {
      // Currently we are in the tap-on phase (the subject was touching the FSR)
      
      // Check whether the force we are currently reading is greater than the maximum force; if so, update the maximum
      if (fsrReading>tap_max_force) {
	tap_max_force_t = current_t;
	tap_max_force   = fsrReading;
      }
      
      // Check whether this may be a tap offset
      if ( (current_t > next_event_embargo_t) && (fsrReading<tap_offset_threshold)) {

	// New Tap Offset
	
	tap_phase = 0; // currently we are in the tap "OFF" phase
	tap_offset_t = current_t;
	
	// don't allow an offset immediately; freeze the phase for a little while
	next_event_embargo_t = current_t + min_tap_off_duration;

	// Send data to the computer!
	send_tap_to_serial();

	// Clear information about the tap so that we are ready for the next tap to occur
	tap_onset_t     = 0;
	tap_offset_t    = 0;
	tap_max_force   = 0;
	tap_max_force_t = 0;
	
      }
      
    }

    
    // Update the loop time
    prev_t = current_t;
  }

  
}





void send_tap_to_serial() {
  /* Sends information about the current tap to the PC through the serial interface */
  char msg[100];
  sprintf(msg, "%d %lu %lu %lu %d %d\n",
	  tap_number,
	  tap_onset_t,
	  tap_offset_t,
	  tap_max_force_t,
	  tap_max_force,
	  missed_frames);
  Serial.print(msg);
  
}