
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





# Python GUI

Requirements: `pyserial` (`pip install pyserial`).




# Log

## 29 Sept 2017
Tinkering a lot to do basic FSR reading. For reasons that I don't understand, it didn't work when I plugged the FSR into 3.3 V (250 mA max) port and AGND (with 1kOhm resistor). It did work when I plugged the power into Vin (which gives nice 5V peak with the digital GND).

Then it also worked when I plugged it into the 3.3V that is next to GND/Program/A14 (and leave the ground as GND).




# TODO

- [ ] Deal with timer overflows (can we set the timer to zero manually?)
- [ ] Fine-tune the resistance so that it yields optimal SNR
- [ ] Communicate tap times to computer


