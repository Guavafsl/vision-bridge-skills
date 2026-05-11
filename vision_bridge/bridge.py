"""
Image routing bridge.

Selects the appropriate vision provider based on the ``VISION_PROVIDER``
environment variable and delegates the analysis call.
"""

from __future__ import annotations

from typing import Optional

from . import config
from .providers import anthropic as _anthropic
from .providers import mimo as _mimo

# Keyed by provider name; .analyze is looked up at call-time so that
# patching vision_bridge.providers.<name>.analyze works in tests.
_PROVIDERS = {
    "anthropic": _anthropic,
    "mimo": _mimo,
}


def analyze_image(
    image_source: str,
    prompt: str = "Describe this image in detail.",
    *,
    provider: Optional[str] = None,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    max_tokens: int = 1024,
) -> str:
    """Route *image_source* to a vision model and return its analysis.

    Parameters
    ----------
    image_source:
        The image to analyse.  Accepted formats:

        * ``http://`` / ``https://`` URL
        * Local file path (e.g. ``"/tmp/photo.jpg"``)
        * ``data:`` URI (e.g. ``"data:image/png;base64,…"``)

    prompt:
        Instruction passed to the vision model together with the image.
        Defaults to ``"Describe this image in detail."``.
    provider:
        Vision backend to use – ``"anthropic"`` or ``"mimo"``.
        Overrides the ``VISION_PROVIDER`` environment variable.
    api_key:
        Provider API key.  Overrides the provider-specific environment
        variable (``ANTHROPIC_API_KEY`` or ``MIMO_API_KEY``).
    model:
        Model identifier.  Overrides the provider-specific environment
        variable (``ANTHROPIC_MODEL`` or ``MIMO_MODEL``).
    max_tokens:
        Maximum tokens to generate in the response.

    Returns
    -------
    str
        The vision model's textual description / answer.

    Raises
    ------
    ValueError
        If *provider* is not one of the supported values, or if the
        required API key is missing.
    """
    selected = (provider or config.VISION_PROVIDER).lower()

    if selected not in _PROVIDERS:
        raise ValueError(
            f"Unsupported vision provider: {selected!r}. "
            f"Choose one of: {sorted(_PROVIDERS)}"
        )

    return _PROVIDERS[selected].analyze(
        image_source,
        prompt,
        api_key=api_key,
        model=model,
        max_tokens=max_tokens,
    )
