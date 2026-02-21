"""Camera control module wrapping Picamera2."""

import logging
import subprocess
import time
from datetime import datetime
from pathlib import Path

from picamera2 import Picamera2

logger = logging.getLogger(__name__)

IR_LED_GPIO = 21


class MeisenCamera:
    """Wrapper around Picamera2 for still image capture."""

    def __init__(
        self,
        width: int = 640,
        height: int = 480,
        exposure_time: int = 50000,
        analogue_gain: float = 1.0,
        brightness: float = 0.3,
        contrast: float = 1.4,
        saturation: float = 0.2,
        sharpness: float = 1.3,
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
        config = self._camera.create_still_configuration(
            main={"size": (self.width, self.height)}
        )
        self._camera.configure(config)
        self._camera.set_controls(
            {
                "AeEnable": True,
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
            ["pinctrl", "set", str(IR_LED_GPIO), "op", state],
            check=False,
        )
        logger.info("IR LED %s", "on" if on else "off")

    def capture(self, output_path: Path) -> str:
        """Capture a still image.

        Returns the timestamp string for the capture.
        """
        self._set_ir_led(True)
        self._camera.start()
        time.sleep(2)  # sensor stabilisation

        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        self._camera.capture_file(str(output_path))

        self._camera.stop()
        self._set_ir_led(False)
        logger.info("Captured image: %s", output_path)
        return timestamp
