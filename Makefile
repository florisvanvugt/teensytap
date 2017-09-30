
default: readme

readme: readme.html
	xdg-open readme.html

readme.html: readme.md misc/github-pandoc.css
	pandoc -f markdown -t html readme.md -s -c misc/github-pandoc.css -o readme.html





upload: teensy_tap.ino
	arduino --upload teensy_tap.ino


