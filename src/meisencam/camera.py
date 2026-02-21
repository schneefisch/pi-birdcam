"""Camera control module wrapping Picamera2."""

import logging
import subprocess
import time
from datetime import datetime
from pathlib import Path

from picamera2 import Picamera2

from meisencam import config

logger = logging.getLogger(__name__)


class MeisenCamera:
    """Wrapper around Picamera2 for still image capture."""

    def __init__(
        self,
        width: int = config.CAMERA_WIDTH,
        height: int = config.CAMERA_HEIGHT,
        exposure_time: int = config.CAMERA_EXPOSURE_TIME,
        analogue_gain: float = config.CAMERA_ANALOGUE_GAIN,
        brightness: float = config.CAMERA_BRIGHTNESS,
        contrast: float = config.CAMERA_CONTRAST,
        saturation: float = config.CAMERA_SATURATION,
        sharpness: float = config.CAMERA_SHARPNESS,
    ):
        self.width = width
        self.height = height
        self.exposure_time = exposure_time
        self.analogue_gain = analogue_gain
        self.brightness = brightness
        self.contrast = contrast
        self.saturation = saturation
        self.sharpness = sharpness

        self._camera = Picamera2()
        time.sleep(1)
        self._configure()
        logger.info("Camera configured (%dx%d)", self.width, self.height)

    def _configure(self) -> None:
        conf = self._camera.create_still_configuration(
            main={"size": (self.width, self.height)}
        )
        self._camera.configure(conf)
        self._camera.set_controls(
            {
                "AeEnable": False,
                "ExposureTime": self.exposure_time,
                "AnalogueGain": self.analogue_gain,
                "AwbEnable": False,
                "ColourGains": (0.8, 1.6),
                "Brightness": self.brightness,
                "Contrast": self.contrast,
                "Saturation": self.saturation,
                "Sharpness": self.sharpness,
            }
        )

    @staticmethod
    def _set_ir_led(on: bool) -> None:
        state = "dh" if on else "dl"
        subprocess.run(
            ["pinctrl", "set", str(config.IR_LED_GPIO), "op", state],
            check=False,
        )
        logger.info("IR LED %s", "on" if on else "off")

    def capture(self, output_path: Path) -> str:
        """Capture a still image.

        Returns the timestamp string for the capture.
        """
        self._set_ir_led(True)
        self._camera.start()
        time.sleep(5)  # sensor stabilisation

        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        self._camera.capture_file(str(output_path))

        self._camera.stop()
        self._set_ir_led(False)
        logger.info("Captured image: %s", output_path)
        return timestamp
