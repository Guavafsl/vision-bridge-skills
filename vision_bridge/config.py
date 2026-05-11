"""
Configuration for vision-bridge.

All settings are read from environment variables so that no credentials
or provider preferences need to be hard-coded.

Environment variables
---------------------
VISION_PROVIDER
    Which vision backend to use.  Accepted values (case-insensitive):
    ``anthropic`` (default) or ``mimo``.

ANTHROPIC_API_KEY
    API key for the Anthropic Messages API.

ANTHROPIC_MODEL
    Anthropic model name (default: ``claude-opus-4-5``).

ANTHROPIC_BASE_URL
    Base URL for the Anthropic API
    (default: ``https://api.anthropic.com``).

MIMO_API_KEY
    API key for the MiMo vision API.

MIMO_MODEL
    MiMo model name (default: ``mimo-vl-7b-rl``).

MIMO_BASE_URL
    Base URL for the MiMo API (default: ``https://api.mimo.ai``).
"""

import os

# ---------------------------------------------------------------------------
# Provider selection
# ---------------------------------------------------------------------------

VISION_PROVIDER: str = os.environ.get("VISION_PROVIDER", "anthropic").lower()

# ---------------------------------------------------------------------------
# Anthropic
# ---------------------------------------------------------------------------

ANTHROPIC_API_KEY: str = os.environ.get("ANTHROPIC_API_KEY", "")
ANTHROPIC_MODEL: str = os.environ.get("ANTHROPIC_MODEL", "claude-opus-4-5")
ANTHROPIC_BASE_URL: str = os.environ.get(
    "ANTHROPIC_BASE_URL", "https://api.anthropic.com"
).rstrip("/")
ANTHROPIC_VERSION: str = "2023-06-01"

# ---------------------------------------------------------------------------
# MiMo
# ---------------------------------------------------------------------------

MIMO_API_KEY: str = os.environ.get("MIMO_API_KEY", "")
MIMO_MODEL: str = os.environ.get("MIMO_MODEL", "mimo-vl-7b-rl")
MIMO_BASE_URL: str = os.environ.get(
    "MIMO_BASE_URL", "https://api.mimo.ai"
).rstrip("/")
