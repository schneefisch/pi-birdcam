"""WebDAV upload to Nextcloud public share."""

import logging
from datetime import datetime
from pathlib import Path

import requests

from meisencam import config

logger = logging.getLogger(__name__)


def upload_image(
    image_path: Path,
    mode: int,
    *,
    webdav_base: str = config.WEBDAV_BASE,
    share_token: str = config.SHARE_TOKEN,
) -> requests.Response | None:
    """Upload an image via WebDAV if motion was detected.

    Args:
        image_path: Path to the image file.
        mode: Motion mode (1 = motion detected, 0 = no motion).
        webdav_base: WebDAV endpoint URL.
        share_token: Nextcloud public share token used as username.

    Returns:
        The HTTP response on success, or None if skipped / file missing.
    """
    if mode < 1:
        logger.info("No motion (mode=%d), skipping upload", mode)
        return None

    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    filename = f"{timestamp}-m{mode}.jpg"
    url = f"{webdav_base}/{filename}"

    logger.info("Uploading %s -> %s", image_path, url)
    try:
        with open(image_path, "rb") as img:
            response = requests.put(
                url, data=img, auth=(share_token, "")
            )
        logger.info("Upload response: %d", response.status_code)
        return response
    except FileNotFoundError:
        logger.error("Image file not found: %s", image_path)
        return None
