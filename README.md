# BSD-REST

This is a simple REST API for BSD

* api.py - is a Python 3 script for uWSGI. It returns JSON objects.
* _bsdgpiomodule.patch - is a patch for freebsd-gpio module

Tested on Raspberry Pi with FreeBSD 10.1

At this time this script reacts on the following requests:

* GET /api/localtime - returns current system time
* GET /api/gpio - list of all GPIO pins with its name, value and configs
* GET /api/gpio/%d - name, value and configs of pin %d
* PUT /api/gpio/%d?value=v - setup value of pin %d to v
* PUT /api/gpio/%d?config=c - setup config of pin %d to c
* GET /api/gpio/%d/name - get name of pin %d
* GET /api/gpio/%d/value - get value of pin %d
* GET /api/gpio/%d/config - get config of pin %d
* GET /api/gpio/%d/caps - get caps of pin %d

