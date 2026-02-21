"""Tests for the upload module."""

from pathlib import Path
from unittest.mock import MagicMock, patch

from meisencam.upload import upload_image


class TestUploadImage:
    def test_skips_upload_when_no_motion(self, tmp_path: Path) -> None:
        image = tmp_path / "test.jpg"
        image.write_bytes(b"fake-jpeg")

        result = upload_image(image, mode=0)

        assert result is None

    @patch("meisencam.upload.requests.put")
    def test_uploads_when_motion_detected(
        self, mock_put: MagicMock, tmp_path: Path
    ) -> None:
        image = tmp_path / "test.jpg"
        image.write_bytes(b"fake-jpeg")
        mock_put.return_value = MagicMock(status_code=201)

        result = upload_image(
            image, mode=1, webdav_base="https://example.com/webdav", share_token="tok"
        )

        assert result is not None
        assert result.status_code == 201
        mock_put.assert_called_once()
        call_kwargs = mock_put.call_args
        assert call_kwargs.kwargs["auth"] == ("tok", "")

    @patch("meisencam.upload.requests.put")
    def test_upload_url_contains_mode(
        self, mock_put: MagicMock, tmp_path: Path
    ) -> None:
        image = tmp_path / "test.jpg"
        image.write_bytes(b"fake-jpeg")
        mock_put.return_value = MagicMock(status_code=201)

        upload_image(
            image, mode=2, webdav_base="https://example.com/webdav", share_token="tok"
        )

        url = mock_put.call_args.args[0]
        assert url.startswith("https://example.com/webdav/")
        assert "-m2.jpg" in url

    def test_returns_none_for_missing_file(self, tmp_path: Path) -> None:
        missing = tmp_path / "nonexistent.jpg"

        result = upload_image(missing, mode=1)

        assert result is None
