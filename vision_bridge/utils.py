"""
Shared helpers used by multiple providers.

All network calls use only the Python standard library (``urllib``).
"""

import base64
import json
import urllib.request
import urllib.error
from typing import Any, Dict


def encode_image_to_base64(image_source: str) -> tuple:
    """Return ``(base64_data, media_type)`` for *image_source*.

    *image_source* may be:

    * An ``http://`` or ``https://`` URL – the image is fetched and
      base64-encoded.
    * A local file path – the file is read and base64-encoded.
    * A ``data:`` URI – the embedded base64 payload is extracted.
    * A raw base64 string (assumed ``image/jpeg`` media type).

    Returns
    -------
    tuple[str, str]
        ``(base64_string, media_type)`` where *base64_string* contains no
        line breaks and *media_type* is e.g. ``"image/jpeg"``.
    """
    if image_source.startswith("data:"):
        # data:<media_type>;base64,<data>
        header, data = image_source.split(",", 1)
        media_type = header.split(";")[0].replace("data:", "")
        return data.strip(), media_type

    if image_source.startswith(("http://", "https://")):
        with urllib.request.urlopen(image_source) as response:  # noqa: S310
            raw = response.read()
            content_type = response.headers.get_content_type() or "image/jpeg"
    else:
        # Treat as a local file path
        with open(image_source, "rb") as fh:
            raw = fh.read()
        content_type = _guess_media_type(image_source)

    return base64.b64encode(raw).decode("ascii"), content_type


def _guess_media_type(path: str) -> str:
    """Infer a media type from the file extension of *path*."""
    lower = path.lower()
    if lower.endswith(".png"):
        return "image/png"
    if lower.endswith(".gif"):
        return "image/gif"
    if lower.endswith(".webp"):
        return "image/webp"
    return "image/jpeg"


def http_post(url: str, headers: Dict[str, str], payload: Any) -> Any:
    """Send a JSON POST request and return the parsed JSON response.

    Raises :class:`urllib.error.HTTPError` on non-2xx responses, attaching
    the response body to the exception for easier debugging.
    """
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=body,
        headers={**headers, "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request) as response:  # noqa: S310
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        try:
            exc.msg = exc.read().decode("utf-8")
        except Exception:
            pass
        raise
