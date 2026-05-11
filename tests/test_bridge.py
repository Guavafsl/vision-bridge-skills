"""
Tests for vision_bridge.bridge (the routing layer).
"""

import base64
import unittest
from unittest.mock import patch


FAKE_B64 = base64.b64encode(b"fake image data").decode("ascii")
FAKE_DATA_URI = f"data:image/jpeg;base64,{FAKE_B64}"


class TestAnalyzeImage(unittest.TestCase):

    def test_routes_to_anthropic_by_default(self):
        import vision_bridge.config as cfg
        original = cfg.VISION_PROVIDER
        cfg.VISION_PROVIDER = "anthropic"
        try:
            with patch(
                "vision_bridge.providers.anthropic.analyze",
                return_value="anthropic result",
            ) as mock_analyze:
                from vision_bridge import analyze_image
                result = analyze_image(FAKE_DATA_URI, api_key="sk-ant-test")
            mock_analyze.assert_called_once()
            self.assertEqual(result, "anthropic result")
        finally:
            cfg.VISION_PROVIDER = original

    def test_routes_to_mimo_when_specified(self):
        with patch(
            "vision_bridge.providers.mimo.analyze",
            return_value="mimo result",
        ) as mock_analyze:
            from vision_bridge import analyze_image
            result = analyze_image(
                FAKE_DATA_URI, provider="mimo", api_key="mimo-key"
            )
        mock_analyze.assert_called_once()
        self.assertEqual(result, "mimo result")

    def test_provider_kwarg_overrides_env(self):
        import vision_bridge.config as cfg
        original = cfg.VISION_PROVIDER
        cfg.VISION_PROVIDER = "anthropic"
        try:
            with patch(
                "vision_bridge.providers.mimo.analyze",
                return_value="overridden",
            ) as mock_mimo:
                from vision_bridge import analyze_image
                result = analyze_image(
                    FAKE_DATA_URI, provider="mimo", api_key="mimo-key"
                )
            mock_mimo.assert_called_once()
            self.assertEqual(result, "overridden")
        finally:
            cfg.VISION_PROVIDER = original

    def test_invalid_provider_raises(self):
        from vision_bridge import analyze_image
        with self.assertRaises(ValueError) as ctx:
            analyze_image(FAKE_DATA_URI, provider="unknown")
        self.assertIn("unknown", str(ctx.exception))

    def test_default_prompt(self):
        with patch(
            "vision_bridge.providers.anthropic.analyze",
            return_value="ok",
        ) as mock_analyze:
            from vision_bridge import analyze_image
            analyze_image(FAKE_DATA_URI, provider="anthropic", api_key="key")

        _img, prompt = mock_analyze.call_args[0]
        self.assertIn("Describe", prompt)

    def test_custom_prompt_forwarded(self):
        with patch(
            "vision_bridge.providers.mimo.analyze",
            return_value="ok",
        ) as mock_analyze:
            from vision_bridge import analyze_image
            analyze_image(
                FAKE_DATA_URI,
                "Count the objects.",
                provider="mimo",
                api_key="key",
            )

        _img, prompt = mock_analyze.call_args[0]
        self.assertEqual(prompt, "Count the objects.")

    def test_max_tokens_forwarded(self):
        with patch(
            "vision_bridge.providers.anthropic.analyze",
            return_value="ok",
        ) as mock_analyze:
            from vision_bridge import analyze_image
            analyze_image(
                FAKE_DATA_URI,
                provider="anthropic",
                api_key="key",
                max_tokens=512,
            )

        kwargs = mock_analyze.call_args[1]
        self.assertEqual(kwargs.get("max_tokens"), 512)


if __name__ == "__main__":
    unittest.main()
