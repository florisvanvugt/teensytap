

# If you want to use whatever arduino is already in your path
ARDUINO := arduino
# If you want to use a custom arduino location:
#ARDUINO := /usr/share/arduino-tinker/arduino




default: gui

readme: readme.html
	xdg-open readme.html

readme.html: readme.md
	pandoc -f markdown -t html readme.md -s -c misc/github-pandoc.css -o readme.html

doc: development.html
	xdg-open development.html

development.html: development.md misc/github-pandoc.css
	pandoc -f markdown -t html development.md -s -c misc/github-pandoc.css -o development.html



.PHONY: teensytap/DeviceID.h # this ensures DeviceID.h will always be re-made

teensytap/DeviceID.h:
	@echo "Determining Device ID"
	@python -c "import time; print('char DEVICE_ID[] = \"%s\";'%time.strftime('%Y/%m/%d %H:%M:%S'))" > teensytap/DeviceID.h
#python -c "import datetime; print(datetime.datetime.strftime('%h'))" 


upload: teensytap/DeviceID.h teensytap/teensytap.ino
	@echo ""
	@echo "### Compiling using $(ARDUINO)"
	@echo ""
	$(ARDUINO) -v --upload teensytap/teensytap.ino


serial:
	cat /dev/ttyACM0


gui:
	python3 gui.py


delay:
	python3 delaydetect.py

