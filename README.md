# pi-light
A customizable Raspberry Pi Zero W nightlight

![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi) [![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

### What is this repository for? ###

I needed a nightlight that could be scheduled and color-synced to a particular sleep/wake hour pattern, for a young restless child, you know? If you're in the same boat, feel free to use this, modify it, and share any improvements.

### How do I get set up? ###

* Grab a [Raspberry Pi Zero W](https://www.raspberrypi.org/products/raspberry-pi-zero-w)
* Plug in a NeoPixel strip to 5V (pin 2), GND (pin 6), and MOSI (pin 19). For reference: [Raspberry Pi Zero W Pinout](https://cdn.sparkfun.com/assets/learn_tutorials/6/7/6/PiZero_1.pdf)
* Clone this repo to the Pi
* Run the following commands:
```bash
poetry install
poetry add RPi.GPIO
ENVIRONMENT=prod poetry run python -m app.main
```

### Who do I talk to? ###

* Peter Gebhard - [github.com/pg](github.com/pg)
