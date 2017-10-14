
The purpose here is to build a Teensy interface that can 
- register taps and
- send the taps to a computer via usb
- deliver auditory feedback and
- play a metronome sound



# General info about Teensy

* https://www.pjrc.com/teensy/loader_cli.html


## Setting up

Install the UDEV rules, i.e.

```
wget https://www.pjrc.com/teensy/49-teensy.rules
sudo cp 49-teensy.rules /etc/udev/rules.d
```


```
git clone https://github.com/PaulStoffregen/teensy_loader_cli.git
```

Edit the `Makefile` (remove the `?` in the equals sign in the Linux line).
Then `make`.

```
./teensy_loader_cli --mcu=mk20dx256 -w blink_slow_Teensy32.hex
```



## Using teensy loader
Following the description here:
https://www.pjrc.com/teensy/loader_linux.html

This requires that you have already compiled a HEX file.




## Teensyduino

I installed the latest Arduino IDE (not through Ubuntu but from the Arduino site https://www.arduino.cc/en/Main/Software

Extract to say `/usr/share` and run `install.sh` to set it up.

Then install the teensyduino add-on, which is downloaded from
https://www.pjrc.com/teensy/td_139/TeensyduinoInstall.linux64

and then run it `chmod +x TeensyduinoInstall.linux64`. Select the folder where you had installed Arduino IDE.


For usage:

https://www.pjrc.com/teensy/td_usage.html

You need to have the teensy loader running, so that the Arduino IDE can communicate.



## Teensyduino command line
It looks like we can then use it from the command line as here:

https://github.com/arduino/Arduino/blob/master/build/shared/manpage.adoc

You can use something like this to upload:
```
arduino --upload read_fsr.ino
```




## Emacs support

Install https://github.com/bookest/arduino-mode

Then add to LISP load path and add following to `.emacs`:
```
(require 'arduino-mode)
(add-to-list 'auto-mode-alist '("\\.ino" . arduino-mode))
```






## Reading serial input

```
cat /dev/ttyACM0
```




## Using FSR
I am using roughly this circuit:

https://learn.adafruit.com/force-sensitive-resistor-fsr/using-an-fsr




## Teensy Audio

https://www.pjrc.com/store/teensy3_audio.html

Note that you cannot use this until you have soldered it fixed to the board.

To play audio, you can use the Teensy Audio library. It doesn't have a lot of documentation though (at present). The documentation that there is is based on a tutorial in which the hardware setup is different (Teensy + Audio but also a bunch of buttons etc.). 



# Python GUI

Requirements: `pyserial` (`pip install pyserial`).




# Soldering

* Lead-based: 650 F (easier).
* Non-lead-based: 750 F





# Log

## 29 Sept 2017
Tinkering a lot to do basic FSR reading. For reasons that I don't understand, it didn't work when I plugged the FSR into 3.3 V (250 mA max) port and AGND (with 1kOhm resistor). It did work when I plugged the power into Vin (which gives nice 5V peak with the digital GND).

Then it also worked when I plugged it into the 3.3V that is next to GND/Program/A14 (and leave the ground as GND).


## 30 Sept 2017
A basic working version for collecting taps. Created a Python GUI to read the tap information live. Nice!

When adding the audio shield, I realise that it will use the A0 pin (as well as A1) so I cannot use it for reading the FSR. No worries, based on their [schematic](https://www.pjrc.com/store/teensy3_audio_pins.png) I think I can use A2 for reading the FSR, it is free.

I am also wondering whether sounds should be played from the SD card or otherwise pre-loaded. It seems to me that you can include sounds as a header so that they are played directly from memory.

Had trouble getting sound output. I think the issue is the Teensy is simply not interfacing with the audio board at all. This may be because I had not soldered it. This seems a good explanation of the soldering [here](https://www.youtube.com/watch?v=37mW1i_oEpA).



## 1 Oct 2017

Soldering Teensy & Audio board together. Checking for short circuits suggests all is well except perhaps the 3.3V pin making contact with the adjacent Teensy pin 23?

Success! Now the SamplePlayer sketch actually works! Yippie.

By the way, I like this wav2sketch thing that allows you to convert a wav file into a C-header that you can compile directly into your program (no need for SD). It just sounds like that can be a faster way.



## 2 Oct 2017

Also soldered connectors for the FSR on to the Teensy. I had to move from A0 for reading the FSR voltage to A3 because A0 was in use. First I didn't get a good reading (just oscillating values), which was fixed when I resoldered the connector.

Downloaded a metronome sound from [here](https://freesound.org/people/digifishmusic/sounds/49115/). Cut it into pieces manually.

You can convert a WAV to C code that you can include directly into the Teensy program hence avoiding the need for the SD card. The code for this is [wav2sketch](https://raw.githubusercontent.com/UECIDE/Teensy3/master/cores/teensy3/files/libraries/Audio/examples/SamplePlayer/wav2sketch/wav2sketch.c). When you run it it will automatically convert all audio files in that directory to C code.

Now trying to figure out a way in which the PC can send instructions for a particular trial to the Teensy. This should involve some very simple data packet, that will then send Teensy on its way to run the trial. I think I would like the Teensy to start in some kind of "listening" state, and then you send it the instructions for a trial and then it runs. It sounds best not to disturb the Teensy during the trial.




## 10 Oct 2017

Wondering whether I can use a different resistor, perhaps to get better SNR when measuring taps. Currently the tap signals I get for reasonable tapping are `~100-160`. Since this is from the function `analogRead`, I suppose it is out of `1024` which means we are using only a tenth of the sensor bandwidth.

Given the wiring, I think we have that $U_f / R_f = U_r / R_r$ where $U_f$ are voltages and $R_f$ resistances of the FSR and $U_r,R_r$ idem for the fixed resistor. The reason is that $U=IR$ and $I$ is constant for the two resistors. Furthermore, since the two resistors are in series, we have that $U_tot = U_r + U_f$.
Given that equation, we want to increase $U_f$, which should mean we should decrease $R_r$. 

However, I seem to be getting a nice signal with a 4.2 kOhm resistor. Anything in that range seems to be doing reasonably well.



## 11 Oct 2017

Trying to get an estimate of false positive rate. For this purpose I let the device sit without forces being applied and took a lot of samples, which I then analyse in `calibrate.R`. This is for the 4.2 kOhm resistor circuit. It seems that any cutoff value of 13 (arbitrary `analogRead` units) gives astronomically small probabilities for false alarms even if you were to measure for 1 hour continuously at 1 kHz.









# TODO

- [x] Deal with timer overflows (can we set the timer to zero manually?)
- [x] Fine-tune the resistance so that it yields optimal SNR
- [x] Communicate tap times to computer
- [x] Communicate metronome times to computer
- [x] Metronome
- [x] Auditory feedback
- [x] Delayed auditory feedback
- [ ] Check that the tap timings actually make sense; perhaps plot them; do we get lots of minimal tap/inter-tap-durations?
- [ ] Make sure participants cannot see the LED, because it blinks in relation to the amount of sound output!
- [x] Currently sound is mono (?) so it will sound in the left ear only for a stereo plug. Use mono2stereo plug?
- [x] Apply communication settings
- [x] Implement # of metronome clicks (and continuation)
- [x] Save data to file
- [x] Enforce logic in GUI, by disabling and enabling buttons depending on the status
- [x] Replace the snare drum file because I don't have the copyright?
- [x] Bug? -- Feedback can occur before tap (new start)
- [x] For Mac OS, allow device selection /dev/tty.usbmodem*
- [ ] Make a device ID (probably just hard-coded)


