"""
MiMo vision provider.

MiMo exposes an OpenAI-compatible ``POST /v1/chat/completions`` endpoint.
Images are passed as ``image_url`` content blocks (base64 data URIs are
supported by the API and avoid any cross-origin download on the server side).

Pure Python – no external dependencies.

Reference: https://github.com/XiaomiMiMo/MiMo
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
    """Analyse *image_source* with the MiMo vision API.

    Parameters
    ----------
    image_source:
        URL, local file path, ``data:`` URI, or raw base64 string.
    prompt:
        Instruction / question to ask the vision model.
    api_key:
        Overrides :data:`~vision_bridge.config.MIMO_API_KEY`.
    model:
        Overrides :data:`~vision_bridge.config.MIMO_MODEL`.
    max_tokens:
        Maximum number of tokens in the model response.

    Returns
    -------
    str
        The text content of the first choice message.
    """
    api_key = api_key or config.MIMO_API_KEY
    if not api_key:
        raise ValueError(
            "MiMo API key is required. "
            "Set the MIMO_API_KEY environment variable."
        )

    model = model or config.MIMO_MODEL
    b64_data, media_type = encode_image_to_base64(image_source)
    data_uri = f"data:{media_type};base64,{b64_data}"

    payload = {
        "model": model,
        "max_tokens": max_tokens,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": data_uri},
                    },
                    {"type": "text", "text": prompt},
                ],
            }
        ],
    }

    headers = {"Authorization": f"Bearer {api_key}"}
    url = f"{config.MIMO_BASE_URL}/v1/chat/completions"
    response = http_post(url, headers, payload)

    choices = response.get("choices", [])
    if choices:
        return choices[0]["message"]["content"]

    raise ValueError(f"Unexpected MiMo response structure: {response}")
