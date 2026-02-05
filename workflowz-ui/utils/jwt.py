from typing import Any


def decode_jwt(token: str) -> dict[str, Any]:
    """Decode JWT token payload without verification (for client-side use)."""
    import base64
    import json

    try:
        payload = token.split(".")[1]
        payload += "=" * (-len(payload) % 4)
        decoded = base64.urlsafe_b64decode(payload.encode("utf-8"))
        return json.loads(decoded.decode("utf-8"))
    except Exception:
        return {}
