"""Tests for the __main__ entry point CLI."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# Mock picamera2 before importing __main__ (not available on macOS)
sys.modules.setdefault("picamera2", MagicMock())

from meisencam.__main__ import main  # noqa: E402


class TestTestMode:
    """Tests for --test flag: capture a single image and exit."""

    @patch("meisencam.__main__.MeisenCamera")
    def test_test_flag_captures_single_image(
        self, mock_camera_cls: MagicMock, tmp_path: Path
    ) -> None:
        output = tmp_path / "test.jpg"
        mock_cam = MagicMock()
        mock_cam.capture.return_value = "20260221-120000"
        mock_camera_cls.return_value = mock_cam

        main(["--test", "--output", str(output)])

        mock_cam.capture.assert_called_once_with(output)

    @patch("meisencam.__main__.MeisenCamera")
    def test_test_flag_does_not_detect_motion(
        self, mock_camera_cls: MagicMock, tmp_path: Path
    ) -> None:
        mock_camera_cls.return_value.capture.return_value = "20260221-120000"

        with patch("meisencam.__main__.detect_motion") as mock_detect:
            main(["--test", "--output", str(tmp_path / "test.jpg")])
            mock_detect.assert_not_called()

    @patch("meisencam.__main__.MeisenCamera")
    def test_test_flag_does_not_upload(
        self, mock_camera_cls: MagicMock, tmp_path: Path
    ) -> None:
        mock_camera_cls.return_value.capture.return_value = "20260221-120000"

        with patch("meisencam.__main__.upload_image") as mock_upload:
            main(["--test", "--output", str(tmp_path / "test.jpg")])
            mock_upload.assert_not_called()

    @patch("meisencam.__main__.MeisenCamera")
    def test_test_flag_uses_default_output_path(
        self, mock_camera_cls: MagicMock
    ) -> None:
        from meisencam.__main__ import CURRENT_IMAGE

        mock_cam = MagicMock()
        mock_cam.capture.return_value = "20260221-120000"
        mock_camera_cls.return_value = mock_cam

        main(["--test"])

        mock_cam.capture.assert_called_once_with(CURRENT_IMAGE)

    @patch("meisencam.__main__.MeisenCamera")
    def test_test_short_flag(
        self, mock_camera_cls: MagicMock, tmp_path: Path
    ) -> None:
        output = tmp_path / "test.jpg"
        mock_cam = MagicMock()
        mock_cam.capture.return_value = "20260221-120000"
        mock_camera_cls.return_value = mock_cam

        main(["-t", "-o", str(output)])

        mock_cam.capture.assert_called_once_with(output)


class TestFullCycle:
    """Tests that the default (no --test) path still runs the full cycle."""

    @patch("meisencam.__main__.upload_image")
    @patch("meisencam.__main__.detect_motion", return_value=5.0)
    @patch("meisencam.__main__.MeisenCamera")
    def test_no_args_runs_full_cycle(
        self,
        mock_camera_cls: MagicMock,
        mock_detect: MagicMock,
        mock_upload: MagicMock,
    ) -> None:
        mock_cam = MagicMock()
        mock_cam.capture.return_value = "20260221-120000"
        mock_camera_cls.return_value = mock_cam
        mock_upload.return_value = None

        main([])

        mock_cam.capture.assert_called_once()
        mock_detect.assert_called_once()
        mock_upload.assert_called_once()
