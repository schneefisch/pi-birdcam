"""Tests for the motion detection module."""

import shutil
from pathlib import Path
from unittest.mock import patch

from PIL import Image

from meisencam.motion import detect_motion


def _create_image(path: Path, colour: int = 128) -> None:
    """Create a small solid-grey test image."""
    img = Image.new("L", (8, 6), colour)
    img.save(path)


def _create_half_changed_image(path: Path, top_colour: int, bottom_colour: int) -> None:
    """Create an image where top half differs from bottom half."""
    img = Image.new("L", (64, 48))
    for y in range(48):
        for x in range(64):
            img.putpixel((x, y), top_colour if y < 24 else bottom_colour)
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

    def test_solid_images_score_100_percent(self, tmp_path: Path) -> None:
        """Two solid images with large difference → all pixels changed → 100%."""
        current = tmp_path / "current.jpg"
        old = tmp_path / "old.jpg"
        _create_image(current, colour=200)
        _create_image(old, colour=100)

        score = detect_motion(current, old)

        # All pixels differ by 100, well above per-pixel threshold (15).
        # Score should be close to 100%.
        assert score > 95.0

    def test_noise_below_pixel_threshold_scores_zero(self, tmp_path: Path) -> None:
        """Pixel differences below the per-pixel threshold should score 0."""
        current = tmp_path / "current.png"
        old = tmp_path / "old.png"
        # Create images with small difference (5), below default pixel threshold (15)
        img_a = Image.new("L", (64, 48), 100)
        img_a.save(current)
        img_b = Image.new("L", (64, 48), 105)
        img_b.save(old)

        with patch("meisencam.motion.cfg") as mock_cfg:
            mock_cfg.MOTION_COMPARE_SIZE_W = 64
            mock_cfg.MOTION_COMPARE_SIZE_H = 48
            mock_cfg.MOTION_PIXEL_THRESHOLD = 15
            mock_cfg.MOTION_BLUR_RADIUS = 2
            mock_cfg.MOTION_THRESHOLD = 5.0
            mock_cfg.MOTION_REF_MAX_AGE_S = 600
            score = detect_motion(current, old)

        assert score == 0.0

    def test_reference_updated_when_motion_detected(self, tmp_path: Path) -> None:
        """Reference image should be updated when motion IS detected."""
        current = tmp_path / "current.jpg"
        old = tmp_path / "old.jpg"
        _create_image(current, colour=200)
        _create_image(old, colour=50)

        old_bytes_before = old.read_bytes()

        score = detect_motion(current, old)

        assert score > 0.0
        # Old image should now be a copy of current (different bytes than before)
        assert old.read_bytes() != old_bytes_before

    def test_reference_not_updated_when_below_threshold(self, tmp_path: Path) -> None:
        """Reference image should NOT be updated when no motion detected."""
        current = tmp_path / "current.png"
        old = tmp_path / "old.png"
        # Use PNG to avoid JPEG artefacts; identical images → score 0
        img = Image.new("L", (64, 48), 100)
        img.save(current)
        img.save(old)

        old_bytes_before = old.read_bytes()

        score = detect_motion(current, old)

        assert score == 0.0
        assert old.read_bytes() == old_bytes_before

    def test_reference_updated_when_max_age_exceeded(self, tmp_path: Path) -> None:
        """Reference should be updated if older than max age, even without motion."""
        current = tmp_path / "current.png"
        old = tmp_path / "old.png"
        img = Image.new("L", (64, 48), 100)
        img.save(current)
        img.save(old)

        with patch("meisencam.motion.cfg") as mock_cfg:
            mock_cfg.MOTION_COMPARE_SIZE_W = 64
            mock_cfg.MOTION_COMPARE_SIZE_H = 48
            mock_cfg.MOTION_PIXEL_THRESHOLD = 15
            mock_cfg.MOTION_BLUR_RADIUS = 2
            mock_cfg.MOTION_THRESHOLD = 5.0
            mock_cfg.MOTION_REF_MAX_AGE_S = 0  # Force max-age refresh
            score = detect_motion(current, old)

        # Score is still 0 (no motion), but reference got updated
        assert score == 0.0

    def test_score_is_percentage_scale(self, tmp_path: Path) -> None:
        """Score should be on a 0-100 percentage scale."""
        current = tmp_path / "current.jpg"
        old = tmp_path / "old.jpg"
        _create_image(current, colour=200)
        _create_image(old, colour=50)

        score = detect_motion(current, old)

        assert 0.0 <= score <= 100.0
