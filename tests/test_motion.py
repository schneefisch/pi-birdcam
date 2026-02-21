"""Tests for the motion detection module."""

import shutil
from pathlib import Path

from PIL import Image

from meisencam.motion import COMPARE_SIZE, detect_motion


def _create_image(path: Path, colour: int = 128) -> None:
    """Create a small solid-grey test image."""
    img = Image.new("L", (8, 6), colour)
    img.save(path)


class TestDetectMotion:
    def test_no_previous_image_returns_zero(self, tmp_path: Path) -> None:
        current = tmp_path / "current.jpg"
        old = tmp_path / "old.jpg"
        _create_image(current, colour=100)

        score = detect_motion(current, old)

        assert score == 0.0
        assert old.exists(), "Should copy current as old when no previous exists"

    def test_identical_images_return_zero(self, tmp_path: Path) -> None:
        current = tmp_path / "current.jpg"
        old = tmp_path / "old.jpg"
        _create_image(current, colour=100)
        shutil.copy2(str(current), str(old))

        score = detect_motion(current, old)

        assert score == 0.0

    def test_different_images_return_positive_score(self, tmp_path: Path) -> None:
        current = tmp_path / "current.jpg"
        old = tmp_path / "old.jpg"
        _create_image(current, colour=200)
        _create_image(old, colour=50)

        score = detect_motion(current, old)

        assert score > 0.0

    def test_score_equals_pixel_difference_for_solid_images(
        self, tmp_path: Path
    ) -> None:
        current = tmp_path / "current.jpg"
        old = tmp_path / "old.jpg"
        _create_image(current, colour=200)
        _create_image(old, colour=100)

        score = detect_motion(current, old)

        # For solid images the score should be close to the colour difference.
        # JPEG compression may introduce minor artefacts.
        assert abs(score - 100) < 5

    def test_old_image_updated_after_detection(self, tmp_path: Path) -> None:
        current = tmp_path / "current.jpg"
        old = tmp_path / "old.jpg"
        _create_image(current, colour=180)
        _create_image(old, colour=50)

        detect_motion(current, old)

        # After detection, old should be a copy of current
        img_old = Image.open(old).convert("L").resize(COMPARE_SIZE)
        img_cur = Image.open(current).convert("L").resize(COMPARE_SIZE)
        for x in range(COMPARE_SIZE[0]):
            for y in range(COMPARE_SIZE[1]):
                assert abs(img_old.getpixel((x, y)) - img_cur.getpixel((x, y))) < 2
