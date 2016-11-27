# -*- coding: utf-8 -*-

import datetime
import flask
import flask_cors
import neopixel
import time


# Configure Flask
app = flask.Flask(__name__)
flask_cors.CORS(app)


# Configure NeoPixel
LED_COUNT      = 59      # Number of LED pixels.
LED_PIN        = 12      # GPIO pin connected to the pixels (must support PWM!).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 5       # DMA channel to use for generating signal (try 5)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)


# NeoPixel LED strip functions

def strip_init():
	"""Initialize and return the NeoPixel LED strip interface object."""
	strip = neopixel.Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS)
	strip.begin()
	return strip


def strip_fill(strip, color):
	"""Immediately display the same color on all LEDs."""
	for i in range(strip.numPixels()):
		strip.setPixelColor(i, color)
	strip.show()


def strip_blink(strip, color, wait_ms=100, iterations=3):
	"""Blink all LEDs simultaneously, then fade out."""
	strip_fill(strip, color)
	for i in range(iterations * 2 - 1):
		if i % 2 == 0:
			strip.setBrightness(LED_BRIGHTNESS)
		else:
			strip.setBrightness(0)
		strip.show()
		time.sleep(wait_ms / 1000.0)
	strip_fade(strip)


def strip_spread(strip, color, wait_ms=10):
	"""Symmetrically spread a color from the middle LED to all LEDs."""
	middle = (strip.numPixels() - 1) / 2
	i = middle
	j = middle
	while i >= 0 and j < strip.numPixels():
		strip.setPixelColor(i, color)
		strip.setPixelColor(j, color)
		i -= 1
		j += 1
		strip.show()
		time.sleep(wait_ms / 1000.0)
	strip_fade(strip)


def strip_fade(strip, wait_ms=10):
	"""Fade out, then reset all LEDs."""
	for i in range(LED_BRIGHTNESS, 0, -5):
		strip.setBrightness(i)
		strip.show()
		time.sleep(wait_ms / 1000.0)
	strip_fill(strip, neopixel.Color(0, 0, 0))
	strip.setBrightness(LED_BRIGHTNESS)
	strip.show()


# Handle requests

if __name__ == '__main__':
	# Init Flask
	app.run()


@app.route("/event/<type>")
def event(type):
	if type == "location_work":
		color = neopixel.Color(100, 255, 0)  # Orange
	elif type == "location_home":
		color = neopixel.Color(100, 0, 0)    # Green
	elif type == "home_work":
		color = neopixel.Color(200, 255, 0)  # Light orange / yellow
	elif type == "work_home":
		color = neopixel.Color(255, 100, 0)  # Light green
	elif type == "calendar":
		color = neopixel.Color(150, 0, 255)  # Blue
	elif type == "settings":
		color = neopixel.Color(0, 255, 50)   # Pink
	else:
		flask.abort(400)

	# At night, return without firing LED strip
	now = datetime.datetime.now()
	if now.isoweekday() < 6: # Weekdays
		if now.hour < 8 or now.hour >= 22:
			return ""
	else: # Weekends
		if now.hour < 10 or now.hour >= 23:
			return ""

	strip = strip_init()
	strip_spread(strip, color)
	return u"💡"


@app.route("/error")
def error():
	color = neopixel.Color(0, 255, 0)  # Red
	
	strip = strip_init()
	strip_blink(strip, color)
	return u"🚨"
