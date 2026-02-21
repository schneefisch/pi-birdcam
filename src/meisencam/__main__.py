"""Entry point for meisencam — runs one capture cycle."""

import logging
from pathlib import Path

from meisencam.camera import MeisenCamera
from meisencam.motion import detect_motion
from meisencam.upload import upload_image

RAMDISK = Path("/mnt/ramdisk")
CURRENT_IMAGE = RAMDISK / "meisencam.jpg"
OLD_IMAGE = RAMDISK / "meisencamalt.jpg"
LOG_FILE = RAMDISK / "meisencam.log"

THRESHOLD = 3.0


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

    camera = MeisenCamera()

    logging.info("Capturing image")
    timestamp = camera.capture(CURRENT_IMAGE)

    logging.info("Detecting motion")
    score = detect_motion(CURRENT_IMAGE, OLD_IMAGE)
    mode = 1 if score > THRESHOLD else 0

    logging.info("Timestamp: %s  Score: %.2f  Mode: %d", timestamp, score, mode)

    logging.info("Uploading image")
    response = upload_image(CURRENT_IMAGE, mode)

    if response is not None:
        with open(LOG_FILE, "a") as f:
            f.write(f"{timestamp};{score};{mode};{response.text}\n")


if __name__ == "__main__":
    main()
