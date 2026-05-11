# Vision Bridge

Route images to a vision-capable model when your primary chat model (e.g., DeepSeek, any text-only LLM) cannot view images directly.

**Two-stage workflow:**
1. Vision model analyzes the image → structured text report
2. Your primary model reviews the report → maps findings to code/actions → executes

Works with any Anthropic Messages API-compatible multimodal model (MiMo, Claude, etc.).

## Quick Start

```bash
# 1. Set your API key
export VISION_API_KEY="your-api-key"

# 2. Analyze an image
python scripts/vision_bridge.py screenshot.png
```

That's it. No dependencies beyond Python standard library.

## Configuration

All settings via environment variables:

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `VISION_API_KEY` | Yes | — | Your vision model API key |
| `VISION_BASE_URL` | No | MiMo V2.5 endpoint | Anthropic-compatible messages API URL |
| `VISION_MODEL` | No | `mimo-v2.5` | Model name |
| `VISION_DOMAIN` | No | — | Domain context injected into every prompt |

### Supported Models

Any Anthropic Messages API-compatible service:

| Provider | `VISION_BASE_URL` | Notes |
|----------|-------------------|-------|
| MiMo V2.5 | `https://token-plan-sgp.xiaomimimo.com/anthropic/v1/messages` | Default |
| Anthropic Claude | `https://api.anthropic.com/v1/messages` | Requires Anthropic API key |
| Custom | Your URL | Any compatible endpoint |

## Usage

```bash
# Deep structured analysis (default)
python scripts/vision_bridge.py image.png

# Quick one-paragraph description
python scripts/vision_bridge.py image.png --brief

# Custom question
python scripts/vision_bridge.py image.png "What errors do you see in this screenshot?"

# Show model's reasoning process
python scripts/vision_bridge.py image.png --verbose

# Inject domain-specific context
python scripts/vision_bridge.py image.png --domain "You are analyzing medical X-ray images. Look for fractures."
```

## Domain Context

For specialized image analysis, provide domain knowledge via `VISION_DOMAIN` env var or `--domain` flag:

```bash
# Persistent (env var)
export VISION_DOMAIN="You are analyzing PCB layouts. Look for trace routing issues."

# One-off (flag)
python scripts/vision_bridge.py pcb.png --domain "Focus on solder pad quality and via placement."
```

The domain context is prepended to every prompt, giving the vision model the specialized vocabulary and failure modes relevant to your field.

## How It Works

```
┌──────────────┐     ┌─────────────────┐     ┌──────────────┐
│  Text-only   │────▶│  vision_bridge   │────▶│   Vision     │
│  LLM         │     │     .py          │     │   Model      │
│              │◀────│                  │◀────│              │
│ Review + act │     │  text report     │     │  Analysis    │
└──────────────┘     └─────────────────┘     └──────────────┘
```

The vision model focuses purely on pixel-level reasoning: what's visible, what's unusual, what patterns exist. It should NOT suggest code changes. Your primary model handles code-level decisions, with full project context that the vision model lacks.

## Requirements

- Python 3.7+ (standard library only — no pip install needed)
- API key for a vision-capable model

## License

MIT
