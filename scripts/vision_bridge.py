"""Vision Bridge: route images to a vision-capable model for visual analysis.

Two-stage workflow:
  1. Vision model: image → structured visual analysis
  2. Text-only model: review analysis → map to code/actions → execute

Usage:
    python vision_bridge.py <image_path>                    # deep analysis
    python vision_bridge.py <image_path> --brief            # quick description
    python vision_bridge.py <image_path> "custom question"  # custom prompt
    python vision_bridge.py <image_path> --verbose          # show thinking
    python vision_bridge.py <image_path> --domain "..."     # inject domain context

Configuration via environment variables:
    VISION_API_KEY      API key for the vision model
    VISION_BASE_URL     API base URL
    VISION_MODEL        Model name (default: mimo-v2.5)
    VISION_DOMAIN       Optional domain context appended to every prompt
"""

import base64
import json
import os
import sys
import urllib.error
import urllib.request

# ── Configuration (env vars with sensible defaults) ──────────────────────────
API_KEY = os.environ.get("VISION_API_KEY", "")
BASE_URL = os.environ.get(
    "VISION_BASE_URL",
    "https://token-plan-sgp.xiaomimimo.com/anthropic/v1/messages",
)
MODEL = os.environ.get("VISION_MODEL", "mimo-v2.5")
DOMAIN_CONTEXT = os.environ.get("VISION_DOMAIN", "")

# ── Generic prompts ─────────────────────────────────────────────────────────
DEEP_ANALYSIS_PROMPT = """\
You are analyzing an image. Provide a structured analysis with these sections:

## 1. Visual Observation
Describe exactly what you see. Be specific about content, layout, colors,
shapes, text, spatial patterns, and any notable details.

## 2. Issue / Anomaly Identification
Identify anything unusual, unexpected, or noteworthy in the image. Rate the
severity of each finding (none / mild / moderate / severe). Point to
specific regions as evidence.

## 3. Pattern / Trend Analysis
If this image is part of a series or represents data over time: what trends
or relationships are visible? How do different regions or elements compare?

## 4. Recommendations
Based on what you observe, what actions or next steps would be most
productive? Be specific and actionable. Focus on outcomes, not code."""

BRIEF_PROMPT = """\
Briefly describe this image: (1) overall content and layout,
(2) key visual elements, (3) anything notable or unusual."""


def _build_prompt(base_prompt, domain=None):
    """Prepend domain context if available."""
    ctx = domain or DOMAIN_CONTEXT
    if ctx:
        return ctx + "\n\n" + base_prompt
    return base_prompt


def image_to_base64(path):
    ext = path.rsplit(".", 1)[-1].lower() if "." in path else "png"
    media_map = {
        "png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg",
        "webp": "image/webp", "gif": "image/gif",
    }
    media_type = media_map.get(ext, "image/png")
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode(), media_type


def analyze_image(image_path, question=None, verbose=False):
    """Send image to the vision model and return analysis text."""
    if not API_KEY:
        return {
            "error": (
                "VISION_API_KEY environment variable is not set.\n"
                "Set it before running: export VISION_API_KEY='your-key'"
            )
        }

    if question is None:
        question = _build_prompt(DEEP_ANALYSIS_PROMPT)

    b64_data, media_type = image_to_base64(image_path)

    payload = {
        "model": MODEL,
        "max_tokens": 3000,
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
                    {"type": "text", "text": question},
                ],
            }
        ],
    }

    req = urllib.request.Request(
        BASE_URL,
        data=json.dumps(payload).encode(),
        headers={
            "x-api-key": API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            result = json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        return {"error": f"HTTP {e.code}: {e.read().decode()[:300]}"}
    except Exception as e:
        return {"error": str(e)}

    answer_parts = []
    thinking_parts = []

    for block in result.get("content", []):
        if block.get("type") == "text":
            answer_parts.append(block["text"])
        elif block.get("type") == "thinking":
            thinking_parts.append(block["thinking"])

    output = "\n\n".join(answer_parts)
    if verbose and thinking_parts:
        output += "\n\n---\n[Model Thinking]\n" + "\n".join(thinking_parts)

    return {"text": output, "usage": result.get("usage", {})}


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python vision_bridge.py <image_path> [question|--brief] [--verbose] [--domain CONTEXT]")
        print()
        print("Environment variables:")
        print("  VISION_API_KEY    API key (required)")
        print("  VISION_BASE_URL   API base URL")
        print("  VISION_MODEL      Model name (default: mimo-v2.5)")
        print("  VISION_DOMAIN     Optional domain context injected into prompts")
        sys.exit(1)

    image_path = sys.argv[1]

    # Parse flags and positional question
    verbose = False
    brief = False
    domain_override = None
    positional = []

    args = sys.argv[2:]
    i = 0
    while i < len(args):
        a = args[i]
        if a == "--verbose":
            verbose = True
            i += 1
        elif a == "--brief":
            brief = True
            i += 1
        elif a == "--domain" and i + 1 < len(args):
            domain_override = args[i + 1]
            i += 2
        else:
            positional.append(a)
            i += 1

    # Build the final question
    if positional:
        question = _build_prompt(" ".join(positional), domain_override)
    elif brief:
        question = _build_prompt(BRIEF_PROMPT, domain_override)
    else:
        question = _build_prompt(DEEP_ANALYSIS_PROMPT, domain_override)

    result = analyze_image(image_path, question, verbose)
    if "error" in result:
        print(f"[Vision Bridge Error] {result['error']}")
    else:
        print(result["text"])
