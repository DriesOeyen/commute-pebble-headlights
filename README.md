# Commute for Pebble (activity indicator LED-strip)
Commute is an application for the Pebble smartwatch that allows users to look up commute times from their current location to home and work.
Integration with Pebble Timeline allows users to receive proactive notifications when it's time to leave for work.
The app is backed by data from the Google Maps API.

This is an optional activity indicator meant to be used with a Raspberry Pi and an attached LED-strip.
The strip will light up with color-coded, animated patterns indicating usage of Commute's server back-end.
All relevant repos:

- :watch: Pebble watch app (required): https://github.com/DriesOeyen/commute-pebble-app/
- :cloud: Server back-end (required): https://github.com/DriesOeyen/commute-pebble-gae/
- :bulb: Activity indicator LED-strip (optional): this repository

## Setup instructions
**Note:** you don't need this repo for a fully functional Commute service. If that's your goal, refer to the repos linked above.
All this repo adds is a neat usage display based on a Raspberry Pi and attached LED-strip.

If you do want to proceed setting up this repo, here's some general pointers:

- The setup was tested on a 1st-gen Raspberry Pi model B+.
- You need an Adafruit NeoPixel-compatible LED strip. Tweak the default config in `app.py`.
- Don't forget to install Python dependencies with `$ pip install -r requirements.txt`. You can use a virtualenv for this if you prefer.
- The LED strip needs its own power supply. The data lines should be attached to the rPi's GPIO. Check the pinout scheme of your rPi model.
- The latest version of this repo used Pub/Sub to communicate with the Commute server back-end. The `master` branch of the server back-end still relies on the deprecated App Engine Channels API. Switch to the `ferrari-6` branch for Pub/Sub support.
- You can use a tool like Supervisor to run this script in the background: http://supervisord.org
