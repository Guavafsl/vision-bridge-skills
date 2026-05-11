"""
Anthropic Messages API vision provider.

Uses the standard ``POST /v1/messages`` endpoint with image content blocks.
Pure Python – no external dependencies.

Reference: https://docs.anthropic.com/en/api/messages
"""

from __future__ import annotations

from typing import Optional

from .. import config
from ..utils import encode_image_to_base64, http_post


def analyze(
    image_source: str,
    prompt: str,
    *,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    max_tokens: int = 1024,
) -> str:
    """Analyse *image_source* with the Anthropic Messages API.

    Parameters
    ----------
    image_source:
        URL, local file path, ``data:`` URI, or raw base64 string.
    prompt:
        Instruction / question to ask the vision model.
    api_key:
        Overrides :data:`~vision_bridge.config.ANTHROPIC_API_KEY`.
    model:
        Overrides :data:`~vision_bridge.config.ANTHROPIC_MODEL`.
    max_tokens:
        Maximum number of tokens in the model response.

    Returns
    -------
    str
        The text content of the first response block.
    """
    api_key = api_key or config.ANTHROPIC_API_KEY
    if not api_key:
        raise ValueError(
            "Anthropic API key is required. "
            "Set the ANTHROPIC_API_KEY environment variable."
        )

    model = model or config.ANTHROPIC_MODEL
    b64_data, media_type = encode_image_to_base64(image_source)

    payload = {
        "model": model,
        "max_tokens": max_tokens,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": b64_data,
                        },
                    },
                    {"type": "text", "text": prompt},
                ],
            }
        ],
    }

    headers = {
        "x-api-key": api_key,
        "anthropic-version": config.ANTHROPIC_VERSION,
    }

    url = f"{config.ANTHROPIC_BASE_URL}/v1/messages"
    response = http_post(url, headers, payload)

    # Extract text from the first content block
    content = response.get("content", [])
    for block in content:
        if block.get("type") == "text":
            return block["text"]

    raise ValueError(f"Unexpected Anthropic response structure: {response}")
