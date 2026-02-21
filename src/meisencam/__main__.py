"""Entry point for meisencam — runs one capture cycle."""

import argparse
import logging
from pathlib import Path

from meisencam import config
from meisencam.camera import MeisenCamera
from meisencam.motion import detect_motion
from meisencam.upload import upload_image

RAMDISK = Path("/mnt/ramdisk")
CURRENT_IMAGE = RAMDISK / "meisencam.jpg"
OLD_IMAGE = RAMDISK / "meisencamalt.jpg"
LOG_FILE = RAMDISK / "meisencam.log"


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Meisencam bird camera")
    parser.add_argument(
        "-t", "--test", action="store_true", help="capture a single test image and exit"
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=CURRENT_IMAGE,
        help="output path for test image (default: %(default)s)",
    )
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

    camera = MeisenCamera()

    if args.test:
        timestamp = camera.capture(args.output)
        logging.info("Test image saved to %s at %s", args.output, timestamp)
        return

    logging.info("Capturing image")
    timestamp = camera.capture(CURRENT_IMAGE)

    logging.info("Detecting motion")
    score = detect_motion(CURRENT_IMAGE, OLD_IMAGE)
    mode = 1 if score > config.MOTION_THRESHOLD else 0

    logging.info("Timestamp: %s  Score: %.2f  Mode: %d", timestamp, score, mode)

    logging.info("Uploading image")
    response = upload_image(CURRENT_IMAGE, mode)

    if response is not None:
        with open(LOG_FILE, "a") as f:
            f.write(f"{timestamp};{score};{mode};{response.text}\n")


if __name__ == "__main__":
    main()
