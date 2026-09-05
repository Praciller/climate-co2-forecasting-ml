from __future__ import annotations

import json
import logging
import re
from collections.abc import Mapping, Sequence
from datetime import datetime, timezone
from typing import Any

LOGGER_NAME = "co2_forecast_api"
SERVICE_NAME = "co2-forecast-api"
REDACTED = "[REDACTED]"
MAX_STRING_LENGTH = 256
MAX_COLLECTION_ITEMS = 20
SENSITIVE_KEY_FRAGMENTS = (
    "authorization",
    "cookie",
    "credential",
    "password",
    "secret",
    "token",
    "api_key",
    "apikey",
    "private_key",
    "access_key",
)
SENSITIVE_VALUE_PATTERNS = (
    re.compile(r"(?i)\bbearer\s+\S+"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"\bgsk_[A-Za-z0-9_-]{12,}\b"),
    re.compile(r"\b(?:sk|csk)-[A-Za-z0-9_-]{12,}\b"),
    re.compile(r"\bAQ\.[A-Za-z0-9_-]{12,}\b"),
)

LOGGER = logging.getLogger(LOGGER_NAME)
if not LOGGER.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(message)s"))
    LOGGER.addHandler(handler)
LOGGER.setLevel(logging.INFO)
LOGGER.propagate = False


def _is_sensitive_key(key: str) -> bool:
    normalized = key.lower().replace("-", "_")
    return any(fragment in normalized for fragment in SENSITIVE_KEY_FRAGMENTS)


def _is_path_key(key: str) -> bool:
    normalized = key.lower().replace("-", "_")
    return normalized in {"path", "file", "filename", "directory", "root", "cwd"} or normalized.endswith(
        ("_path", "_file", "_dir", "_directory")
    )


def _sanitize_value(value: Any, *, key: str | None = None) -> Any:
    if key is not None and (_is_sensitive_key(key) or _is_path_key(key)):
        return REDACTED
    if value is None or isinstance(value, (bool, int, float)):
        return value
    if isinstance(value, str):
        if any(pattern.search(value) for pattern in SENSITIVE_VALUE_PATTERNS):
            return REDACTED
        if len(value) <= MAX_STRING_LENGTH:
            return value
        return f"{value[:MAX_STRING_LENGTH]}..."
    if isinstance(value, Mapping):
        return {
            str(child_key): _sanitize_value(child_value, key=str(child_key))
            for child_key, child_value in list(value.items())[:MAX_COLLECTION_ITEMS]
        }
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [
            _sanitize_value(item)
            for item in list(value)[:MAX_COLLECTION_ITEMS]
        ]
    return f"<{type(value).__name__}>"


def build_event(
    event: str,
    *,
    level: str = "INFO",
    component: str = "api",
    **context: Any,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "level": level.upper(),
        "service": SERVICE_NAME,
        "component": component,
        "event": event,
    }
    payload.update(
        {
            key: _sanitize_value(value, key=key)
            for key, value in context.items()
            if value is not None
        }
    )
    return payload


def format_event(
    event: str,
    *,
    level: str = "INFO",
    component: str = "api",
    **context: Any,
) -> str:
    return json.dumps(
        build_event(event, level=level, component=component, **context),
        separators=(",", ":"),
        sort_keys=True,
    )


def emit_event(
    event: str,
    *,
    level: str = "INFO",
    component: str = "api",
    **context: Any,
) -> None:
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    LOGGER.log(
        numeric_level,
        format_event(event, level=level, component=component, **context),
    )
