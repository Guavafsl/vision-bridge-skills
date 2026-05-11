"""
Tests for vision_bridge.providers.anthropic
"""

import base64
import json
import unittest
from unittest.mock import MagicMock, patch


FAKE_B64 = base64.b64encode(b"\xff\xd8\xff fake jpeg").decode("ascii")
FAKE_DATA_URI = f"data:image/jpeg;base64,{FAKE_B64}"


def _anthropic_success_response(text: str) -> dict:
    return {
        "id": "msg_abc",
        "type": "message",
        "role": "assistant",
        "content": [{"type": "text", "text": text}],
        "model": "claude-opus-4-5",
        "stop_reason": "end_turn",
        "usage": {"input_tokens": 10, "output_tokens": 20},
    }


class TestAnthropicAnalyze(unittest.TestCase):

    def _call(self, response_text: str, **kwargs):
        """Call providers.anthropic.analyze with a mocked HTTP layer."""
        from vision_bridge.providers.anthropic import analyze

        with patch(
            "vision_bridge.providers.anthropic.http_post",
            return_value=_anthropic_success_response(response_text),
        ) as mock_post:
            result = analyze(
                FAKE_DATA_URI,
                "Describe this image.",
                api_key="sk-ant-test",
                **kwargs,
            )
        return result, mock_post

    def test_returns_text(self):
        result, _ = self._call("A sunny beach.")
        self.assertEqual(result, "A sunny beach.")

    def test_payload_structure(self):
        _, mock_post = self._call("ok")
        _url, _headers, payload = mock_post.call_args[0]
        messages = payload["messages"]
        self.assertEqual(len(messages), 1)
        content = messages[0]["content"]
        # First block: image
        self.assertEqual(content[0]["type"], "image")
        self.assertEqual(content[0]["source"]["type"], "base64")
        self.assertEqual(content[0]["source"]["media_type"], "image/jpeg")
        # Second block: text
        self.assertEqual(content[1]["type"], "text")
        self.assertEqual(content[1]["text"], "Describe this image.")

    def test_correct_url(self):
        _, mock_post = self._call("ok")
        url = mock_post.call_args[0][0]
        self.assertTrue(url.endswith("/v1/messages"), url)

    def test_api_key_in_header(self):
        _, mock_post = self._call("ok")
        headers = mock_post.call_args[0][1]
        self.assertEqual(headers["x-api-key"], "sk-ant-test")
        self.assertIn("anthropic-version", headers)

    def test_model_override(self):
        _, mock_post = self._call("ok", model="claude-haiku-4-5")
        payload = mock_post.call_args[0][2]
        self.assertEqual(payload["model"], "claude-haiku-4-5")

    def test_missing_api_key_raises(self):
        from vision_bridge.providers.anthropic import analyze
        import vision_bridge.config as cfg

        original = cfg.ANTHROPIC_API_KEY
        cfg.ANTHROPIC_API_KEY = ""
        try:
            with self.assertRaises(ValueError, msg="Should raise when no API key"):
                analyze(FAKE_DATA_URI, "prompt")
        finally:
            cfg.ANTHROPIC_API_KEY = original

    def test_unexpected_response_raises(self):
        from vision_bridge.providers.anthropic import analyze

        with patch(
            "vision_bridge.providers.anthropic.http_post",
            return_value={"content": []},
        ):
            with self.assertRaises(ValueError):
                analyze(FAKE_DATA_URI, "prompt", api_key="sk-ant-test")


if __name__ == "__main__":
    unittest.main()
