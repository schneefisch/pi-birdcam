#!/usr/bin/python
# meisentest.py
# Erster Test
from picamera2 import Picamera2
import time
# Voreinstellungen
WIDTH=320
HEIGHT=240
FONTSIZE=20

# initialiye picam
picam2 = Picamera2()
preview_config = picam2.create_preview_configuration(main={"size": (320, 240)})
picam2.configure(preview_config)
picam2.set_controls({"Brightness": 0.6}) # 60% brightness

# start camera
picam2.start()

# Capture image
localpicname = '/mnt/ramdisk/meisencam.jpg'
picam2.capture_file(localpicname)

timestamp = time.strftime("%Y%d%m-%H%M%S")
print(timestamp)

# Stop camera
picam2.stop()
