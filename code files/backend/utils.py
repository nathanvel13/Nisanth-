"""Small parsing and text utility helpers."""
from __future__ import annotations

import json
import re


def truncate(text: str, limit: int = 8000) -> str:
    text = text.strip()
    if len(text) <= limit:
        return text
    return text[:limit].rstrip() + "\n[content truncated]"


def clean_json_block(text: str) -> str:
    """Remove Markdown fences and isolate the first JSON object/array."""
    cleaned = text.strip().replace("\ufeff", "")
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    cleaned = cleaned.strip()

    if cleaned.startswith(("{", "[")):
        return cleaned

    # Models occasionally add a short sentence before JSON.
    object_start = cleaned.find("{")
    array_start = cleaned.find("[")
    starts = [i for i in (object_start, array_start) if i >= 0]
    if not starts:
        return cleaned
    start = min(starts)
    candidate = cleaned[start:]

    # Trim trailing prose after a balanced JSON object/array.
    for end in range(len(candidate), 0, -1):
        fragment = candidate[:end].rstrip()
        if fragment.endswith(("}", "]")):
            try:
                json.loads(fragment)
                return fragment
            except json.JSONDecodeError:
                continue
    return candidate
