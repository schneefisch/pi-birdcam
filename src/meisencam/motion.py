"""Motion detection by comparing consecutive images.

Uses per-pixel thresholding with percentage-of-changed-pixels scoring.
Instead of averaging pixel differences (which mixes motion signal with
sensor noise), this counts what percentage of pixels changed more than
a noise floor — cleanly separating localised motion from distributed
sensor noise.
"""

import logging
import shutil
import time
from pathlib import Path

from PIL import Image, ImageFilter

from meisencam import config as cfg

logger = logging.getLogger(__name__)

_ref_update_time: float = 0.0


def detect_motion(current_path: Path, old_path: Path) -> float:
    """Compare two images and return a motion score (0-100).

    The score is the percentage of pixels whose absolute difference
    exceeds the per-pixel noise threshold, after downscaling and
    Gaussian blur.

    Reference image update policy:
    - Updated when motion IS detected (score > threshold)
    - Updated when reference is older than max age (gradual lighting)
    - NOT updated on no-motion frames (prevents noise drift)

    If no previous image exists, copies the current image and returns 0.
    """
    global _ref_update_time

    try:
        img_new = Image.open(current_path).convert("L")
        img_old = Image.open(old_path).convert("L")
    except FileNotFoundError:
        logger.info("No previous image found, initialising with current image")
        shutil.copy2(str(current_path), str(old_path))
        _ref_update_time = time.time()
        return 0.0

    compare_size = (cfg.MOTION_COMPARE_SIZE_W, cfg.MOTION_COMPARE_SIZE_H)

    img_new = img_new.resize(compare_size)
    img_old = img_old.resize(compare_size)

    if cfg.MOTION_BLUR_RADIUS > 0:
        img_new = img_new.filter(ImageFilter.GaussianBlur(radius=cfg.MOTION_BLUR_RADIUS))
        img_old = img_old.filter(ImageFilter.GaussianBlur(radius=cfg.MOTION_BLUR_RADIUS))

    pixels_new = img_new.tobytes()
    pixels_old = img_old.tobytes()
    total_pixels = len(pixels_new)

    changed = sum(
        1 for pn, po in zip(pixels_new, pixels_old) if abs(pn - po) > cfg.MOTION_PIXEL_THRESHOLD
    )

    score = (changed / total_pixels) * 100.0

    # Update reference image based on policy
    motion_detected = score > cfg.MOTION_THRESHOLD
    ref_age = time.time() - _ref_update_time if _ref_update_time > 0 else 0.0
    ref_expired = _ref_update_time > 0 and ref_age > cfg.MOTION_REF_MAX_AGE_S

    if motion_detected or ref_expired or _ref_update_time == 0.0:
        shutil.copy2(str(current_path), str(old_path))
        _ref_update_time = time.time()
        if ref_expired and not motion_detected:
            logger.info("Reference image refreshed after %.0fs (max age)", ref_age)

    logger.info("Motion score: %.2f%% (%d/%d pixels changed)", score, changed, total_pixels)
    return score
