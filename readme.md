# Teensy Tap

A framework for running sensorimotor synchronisation experiment. The framework is based on Teensy and the Audio Adapter, which are inexpensive and readily available for purchase at many retailers internationally. The code provided here will allow the Teensy to record finger tapping and deliver auditory feedback, optinally with a pre-specified delay, and simultaneously present metronome click sounds. Data is communicated to the computer via USB for offline analysis.

[Demonstration video](https://vimeo.com/236833791)

## Requirements

### Hardware
* [Teensy 3.2](https://www.pjrc.com/store/teensy32.html) (may also work with later versions)
* [Audio Adapter](https://www.pjrc.com/store/teensy3_audio.html) for Teensy
* FSR sensor (Force-sensitive resistor)
* A few wires and a resistor

### Software
* Python 3
* `pyserial` module (use `pip install pyserial`)

### Development software
The following software is required only once for uploading the code to Teensy. From then on you can use it on any computer that fulfills the above software requirements.
* Arduino IDE
* Teensyduino extension for Arduino IDE



## Usage

### Building the circuit
Refer to the circuit diagram `wiring.svg` included here.

1. Solder the Teensy and the Audio Board together. You have to solder only the pins marked in the wiring diagram (to save time).

2. Solder the wires to the resistor and FSR as indicated in `wiring.svg`. 

That's it!



### Uploading the Teensy code
You can either open the `teensytap/teensytap.ino` script in the Arduino IDE and then upload it from there (see the Teensyduino documentation for how this works). Or, if you have a good build environment, you can simply run:

```
make upload
```

### Running
Run the GUI script:

`python3 gui.py`





