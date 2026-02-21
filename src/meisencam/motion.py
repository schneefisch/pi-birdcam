"""Motion detection by comparing consecutive images."""

import logging
import shutil
from pathlib import Path

from PIL import Image

logger = logging.getLogger(__name__)

COMPARE_SIZE = (4, 3)


def detect_motion(current_path: Path, old_path: Path) -> float:
    """Compare two images and return a motion score.

    The score is the average absolute pixel difference (0-255) between
    thumbnail versions of the current and previous image. A higher value
    means more change between frames.

    If no previous image exists, copies the current image and returns 0.
    After comparison the current image is copied over the old image so
    the next call compares against it.
    """
    try:
        img_new = Image.open(current_path).convert("L")
        img_old = Image.open(old_path).convert("L")
    except FileNotFoundError:
        logger.info("No previous image found, initialising with current image")
        shutil.copy2(str(current_path), str(old_path))
        return 0.0

    img_new = img_new.resize(COMPARE_SIZE)
    img_old = img_old.resize(COMPARE_SIZE)

    diff = 0
    for x in range(COMPARE_SIZE[0]):
        for y in range(COMPARE_SIZE[1]):
            diff += abs(img_new.getpixel((x, y)) - img_old.getpixel((x, y)))

    score = diff / (COMPARE_SIZE[0] * COMPARE_SIZE[1])

    shutil.copy2(str(current_path), str(old_path))
    logger.info("Motion score: %.2f", score)
    return score
