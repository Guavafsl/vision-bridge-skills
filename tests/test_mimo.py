"""
Tests for vision_bridge.providers.mimo
"""

import base64
import unittest
from unittest.mock import patch


FAKE_B64 = base64.b64encode(b"\xff\xd8\xff fake jpeg").decode("ascii")
FAKE_DATA_URI = f"data:image/jpeg;base64,{FAKE_B64}"


def _mimo_success_response(text: str) -> dict:
    return {
        "id": "chatcmpl-xyz",
        "object": "chat.completion",
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": text},
                "finish_reason": "stop",
            }
        ],
        "usage": {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
    }


class TestMimoAnalyze(unittest.TestCase):

    def _call(self, response_text: str, **kwargs):
        from vision_bridge.providers.mimo import analyze

        with patch(
            "vision_bridge.providers.mimo.http_post",
            return_value=_mimo_success_response(response_text),
        ) as mock_post:
            result = analyze(
                FAKE_DATA_URI,
                "What is in this image?",
                api_key="mimo-test-key",
                **kwargs,
            )
        return result, mock_post

    def test_returns_text(self):
        result, _ = self._call("A cat on a mat.")
        self.assertEqual(result, "A cat on a mat.")

    def test_payload_structure(self):
        _, mock_post = self._call("ok")
        _url, _headers, payload = mock_post.call_args[0]
        messages = payload["messages"]
        self.assertEqual(len(messages), 1)
        content = messages[0]["content"]
        # First block: image_url
        self.assertEqual(content[0]["type"], "image_url")
        self.assertIn("data:image/jpeg;base64,", content[0]["image_url"]["url"])
        # Second block: text
        self.assertEqual(content[1]["type"], "text")
        self.assertEqual(content[1]["text"], "What is in this image?")

    def test_correct_url(self):
        _, mock_post = self._call("ok")
        url = mock_post.call_args[0][0]
        self.assertTrue(url.endswith("/v1/chat/completions"), url)

    def test_bearer_auth_header(self):
        _, mock_post = self._call("ok")
        headers = mock_post.call_args[0][1]
        self.assertEqual(headers["Authorization"], "Bearer mimo-test-key")

    def test_model_override(self):
        _, mock_post = self._call("ok", model="mimo-vl-7b-rl-custom")
        payload = mock_post.call_args[0][2]
        self.assertEqual(payload["model"], "mimo-vl-7b-rl-custom")

    def test_missing_api_key_raises(self):
        from vision_bridge.providers.mimo import analyze
        import vision_bridge.config as cfg

        original = cfg.MIMO_API_KEY
        cfg.MIMO_API_KEY = ""
        try:
            with self.assertRaises(ValueError):
                analyze(FAKE_DATA_URI, "prompt")
        finally:
            cfg.MIMO_API_KEY = original

    def test_unexpected_response_raises(self):
        from vision_bridge.providers.mimo import analyze

        with patch(
            "vision_bridge.providers.mimo.http_post",
            return_value={"choices": []},
        ):
            with self.assertRaises(ValueError):
                analyze(FAKE_DATA_URI, "prompt", api_key="mimo-key")


if __name__ == "__main__":
    unittest.main()
