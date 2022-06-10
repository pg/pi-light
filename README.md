# pi-light
A customizable Raspberry Pi Zero W nightlight

![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

### What is this repository for? ###

* Quick summary
* Version
* [Learn Markdown](https://bitbucket.org/tutorials/markdowndemo)

### How do I get set up? ###

* Summary of set up
* Configuration
* Dependencies
* Database configuration
* How to run tests
* Deployment instructions

[Raspberry Pi Zero W](https://www.raspberrypi.org/products/raspberry-pi-zero-w)

[Raspberry Pi Zero W Pinout](https://cdn.sparkfun.com/assets/learn_tutorials/6/7/6/PiZero_1.pdf)

Plug in NeoPixel strip to 5V (pin 2), GND (pin 6), and MOSI (pin 19)

```bash
poetry install
poetry add RPi.GPIO
ENVIRONMENT=prod poetry run python -m app.main
```

... update .env file to pull in ENVIRONMENT=prod...

### Contribution guidelines ###

* Writing tests
* Code review
* Other guidelines

### Who do I talk to? ###

* Repo owner or admin
* Other community or team contact
* Other community or team contact
