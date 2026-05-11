"""
vision_bridge – Route images to external vision models for analysis.

Quick start
-----------
>>> import os
>>> os.environ["VISION_PROVIDER"] = "anthropic"       # or "mimo"
>>> os.environ["ANTHROPIC_API_KEY"] = "sk-ant-..."
>>>
>>> from vision_bridge import analyze_image
>>> text = analyze_image("https://example.com/photo.jpg")
>>> print(text)

Configuration
-------------
See :mod:`vision_bridge.config` for all supported environment variables.
"""

from .bridge import analyze_image

__all__ = ["analyze_image"]
