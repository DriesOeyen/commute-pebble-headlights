# -*- coding: utf-8 -*-

"""Commute Headlights: listens for Pub/Sub events and triggers LED strip."""

import datetime
import neopixel
import time
from google.cloud import pubsub


# Configure NeoPixel
LED_COUNT = 59      # Number of LED pixels.
LED_PIN = 12      # GPIO pin connected to the pixels (must support PWM!).
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA = 5       # DMA channel to use for generating signal (try 5)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT = False   # True to invert the signal (when using NPN transistor level shift)

# Configure Pub/Sub
PUBSUB_PROJECT = "commute-pebble"
PUBSUB_SUBSCRIPTION = "headlights"

# Commute defines
REQUEST_TYPE_LOCATION = "0"
REQUEST_TYPE_HOME = "1"
REQUEST_TYPE_WORK = "2"


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


# Listen for and handle Commute events

def fire_event(event_type):
    """Display a Commute event on the LED strip."""
    if event_type == "location_work":
        color = neopixel.Color(100, 255, 0)  # Orange
    elif event_type == "location_home":
        color = neopixel.Color(100, 0, 0)    # Green
    elif event_type == "home_work":
        color = neopixel.Color(200, 255, 0)  # Light orange / yellow
    elif event_type == "work_home":
        color = neopixel.Color(255, 100, 0)  # Light green
    elif event_type == "calendar":
        color = neopixel.Color(150, 0, 255)  # Blue
    elif event_type == "settings":
        color = neopixel.Color(0, 255, 50)   # Pink
    elif event_type == "error":
        color = neopixel.Color(0, 255, 0)  # Red
    else:
        return

    # At night, return without firing LED strip
    now = datetime.datetime.now()
    if now.isoweekday() < 6:  # Weekdays
        if now.hour < 8 or now.hour >= 22:
            return
    else:  # Weekends
        if now.hour < 10 or now.hour >= 23:
            return

    strip = strip_init()
    if event_type == "error":
        strip_blink(strip, color)
    else:
        strip_spread(strip, color)


def handle_event(e):
    """Handle an incoming Commute event."""
    # Identify event
    if e.action == "directions":
        if e.orig == REQUEST_TYPE_LOCATION and e.dest == REQUEST_TYPE_WORK:
            event_type = "location_work"
        elif e.orig == REQUEST_TYPE_LOCATION and e.dest == REQUEST_TYPE_HOME:
            event_type = "location_home"
        elif e.orig == REQUEST_TYPE_HOME and e.dest == REQUEST_TYPE_WORK:
            event_type = "home_work"
        elif e.orig == REQUEST_TYPE_WORK and e.dest == REQUEST_TYPE_HOME:
            event_type = "work_home"
        else:
            return
    else:
        event_type = e.action

    # Fire event on LED strip
    fire_event(event_type)


def pubsub_listen(project, subscription_name):
    """Listen for Commute events on Pub/Sub."""
    subscriber = pubsub.SubscriberClient()
    subscription_path = subscriber.subscription_path(project, subscription_name)

    def pubsub_event(message):
        event = message.attributes
        handle_event(event)
        message.ack()

    # Limit the subscriber to only have 1 outstanding messages at a time.
    flow_control = pubsub.types.FlowControl(max_messages=1)
    subscriber.subscribe(subscription_path, callback=pubsub_event, flow_control=flow_control)

    # The subscriber is non-blocking, so we must keep the main thread from
    # exiting to allow it to process messages in the background.
    print('Listening for events on {}'.format(subscription_path))
    while True:
        time.sleep(60)


# Start Pub/Sub listen loop
pubsub_listen(PUBSUB_PROJECT, PUBSUB_SUBSCRIPTION)
