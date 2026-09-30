"""Educational text summarization logic."""
from __future__ import annotations

from backend.gemini_client import client
from backend.utils import truncate


def summarize_text(text: str) -> tuple[str, str]:
    text = text.strip()
    if not text:
        raise ValueError("Please enter text to summarize.")

    result = client.generate(
        "Summarize this educational passage:\n\n" + truncate(text, 18000),
        system_instruction=(
            "Create a concise, student-friendly summary. Preserve the main facts, "
            "definitions, causes/effects, names, dates, and important terms. Use headings "
            "or bullets when they improve readability. Do not add unsupported facts."
        ),
        temperature=0.2,
        max_output_tokens=1200,
    )
    return result.text, result.model
