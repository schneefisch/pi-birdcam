"""Centralised configuration loaded from environment / .env file."""

import os
from pathlib import Path

ENV_FILE = Path("/mnt/ramdisk/.env")


def _load_env_file(path: Path = ENV_FILE) -> None:
    """Load key=value pairs from an env file into os.environ."""
    if not path.is_file():
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            key, _, value = line.partition("=")
            if key and value:
                os.environ.setdefault(key.strip(), value.strip())


_load_env_file()


def _int(key: str, default: int) -> int:
    return int(os.environ.get(key, default))


def _float(key: str, default: float) -> float:
    return float(os.environ.get(key, default))


# -- Camera ------------------------------------------------------------------
CAMERA_WIDTH = _int("MEISENCAM_WIDTH", 640)
CAMERA_HEIGHT = _int("MEISENCAM_HEIGHT", 480)
CAMERA_EXPOSURE_TIME = _int("MEISENCAM_EXPOSURE_TIME", 200000)
CAMERA_ANALOGUE_GAIN = _float("MEISENCAM_ANALOGUE_GAIN", 8.0)
CAMERA_BRIGHTNESS = _float("MEISENCAM_BRIGHTNESS", 0.3)
CAMERA_CONTRAST = _float("MEISENCAM_CONTRAST", 1.4)
CAMERA_SATURATION = _float("MEISENCAM_SATURATION", 0.2)
CAMERA_SHARPNESS = _float("MEISENCAM_SHARPNESS", 1.3)
IR_LED_GPIO = _int("MEISENCAM_IR_LED_GPIO", 21)

# -- Motion -------------------------------------------------------------------
MOTION_THRESHOLD = _float("MEISENCAM_MOTION_THRESHOLD", 3.0)

# -- Upload -------------------------------------------------------------------
WEBDAV_BASE = os.environ.get(
    "MEISENCAM_WEBDAV_BASE",
    "https://nc-6283277816195226543.nextcloud-ionos.com/public.php/webdav",
)
SHARE_TOKEN = os.environ.get("MEISENCAM_SHARE_TOKEN", "")
