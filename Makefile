
default: gui

readme: development.html
	xdg-open development.html

development.html: development.md misc/github-pandoc.css
	pandoc -f markdown -t html development.md -s -c misc/github-pandoc.css -o development.html




upload: teensytap/teensytap.ino
	arduino --upload teensytap/teensytap.ino


serial:
	cat /dev/ttyACM0


gui:
	python3 gui.py
