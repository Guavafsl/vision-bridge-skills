"""
Tests for vision_bridge.utils – image encoding helpers.
"""

import base64
import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch


class TestEncodeImageToBase64(unittest.TestCase):
    """encode_image_to_base64 should handle every supported source format."""

    def setUp(self):
        from vision_bridge.utils import encode_image_to_base64
        self.encode = encode_image_to_base64

    # ------------------------------------------------------------------
    # data: URI
    # ------------------------------------------------------------------

    def test_data_uri_jpeg(self):
        raw_b64 = base64.b64encode(b"\xff\xd8\xff").decode("ascii")
        data_uri = f"data:image/jpeg;base64,{raw_b64}"
        b64, media_type = self.encode(data_uri)
        self.assertEqual(b64, raw_b64)
        self.assertEqual(media_type, "image/jpeg")

    def test_data_uri_png(self):
        raw_b64 = base64.b64encode(b"\x89PNG").decode("ascii")
        data_uri = f"data:image/png;base64,{raw_b64}"
        b64, media_type = self.encode(data_uri)
        self.assertEqual(media_type, "image/png")

    # ------------------------------------------------------------------
    # Local file
    # ------------------------------------------------------------------

    def test_local_file_jpeg(self):
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as fh:
            fh.write(b"\xff\xd8\xff image bytes")
            tmp_path = fh.name
        try:
            b64, media_type = self.encode(tmp_path)
            self.assertEqual(media_type, "image/jpeg")
            self.assertEqual(base64.b64decode(b64), b"\xff\xd8\xff image bytes")
        finally:
            os.unlink(tmp_path)

    def test_local_file_png(self):
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as fh:
            fh.write(b"\x89PNG bytes")
            tmp_path = fh.name
        try:
            _, media_type = self.encode(tmp_path)
            self.assertEqual(media_type, "image/png")
        finally:
            os.unlink(tmp_path)

    def test_local_file_gif(self):
        with tempfile.NamedTemporaryFile(suffix=".gif", delete=False) as fh:
            fh.write(b"GIF89a")
            tmp_path = fh.name
        try:
            _, media_type = self.encode(tmp_path)
            self.assertEqual(media_type, "image/gif")
        finally:
            os.unlink(tmp_path)

    def test_local_file_webp(self):
        with tempfile.NamedTemporaryFile(suffix=".webp", delete=False) as fh:
            fh.write(b"RIFF....WEBP")
            tmp_path = fh.name
        try:
            _, media_type = self.encode(tmp_path)
            self.assertEqual(media_type, "image/webp")
        finally:
            os.unlink(tmp_path)

    # ------------------------------------------------------------------
    # HTTP URL (mocked)
    # ------------------------------------------------------------------

    def test_http_url(self):
        mock_response = MagicMock()
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_response.read.return_value = b"\xff\xd8\xff"
        mock_response.headers.get_content_type.return_value = "image/jpeg"

        with patch("urllib.request.urlopen", return_value=mock_response):
            b64, media_type = self.encode("https://example.com/img.jpg")

        self.assertEqual(media_type, "image/jpeg")
        self.assertEqual(base64.b64decode(b64), b"\xff\xd8\xff")


class TestHttpPost(unittest.TestCase):
    """http_post should serialise payload and return parsed JSON."""

    def setUp(self):
        from vision_bridge.utils import http_post
        self.http_post = http_post

    def _make_mock_response(self, data: dict, status: int = 200):
        import json
        mock_response = MagicMock()
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_response.read.return_value = json.dumps(data).encode("utf-8")
        mock_response.status = status
        return mock_response

    def test_successful_post(self):
        resp_data = {"result": "ok"}
        mock_resp = self._make_mock_response(resp_data)
        with patch("urllib.request.urlopen", return_value=mock_resp):
            result = self.http_post(
                "https://api.example.com/endpoint",
                {"Authorization": "Bearer token"},
                {"key": "value"},
            )
        self.assertEqual(result, resp_data)

    def test_http_error_raises(self):
        import urllib.error
        exc = urllib.error.HTTPError(
            url="https://api.example.com",
            code=401,
            msg="Unauthorized",
            hdrs=None,
            fp=None,
        )
        with patch("urllib.request.urlopen", side_effect=exc):
            with self.assertRaises(urllib.error.HTTPError):
                self.http_post(
                    "https://api.example.com/endpoint",
                    {"Authorization": "Bearer bad"},
                    {},
                )


if __name__ == "__main__":
    unittest.main()
