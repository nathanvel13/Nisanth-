"""Concept explanation logic with an optional LaMini local provider."""
from __future__ import annotations

from functools import lru_cache

from backend.config import settings
from backend.gemini_client import client
from backend.utils import truncate


@lru_cache(maxsize=1)
def _local_pipeline():
    try:
        from transformers import pipeline
    except ImportError as exc:
        raise RuntimeError(
            "Local explanation mode needs transformers/torch. Install backend/requirements-local.txt."
        ) from exc

    return pipeline("text2text-generation", model=settings.local_explain_model, device=-1)


def _explain_with_local(topic: str) -> str:
    generator = _local_pipeline()
    prompt = (
        "Explain the educational topic below in simple language. Use a short definition, "
        "2-4 key points, and one everyday example.\n\nTopic: " + truncate(topic, 5000)
    )
    output = generator(prompt, max_new_tokens=260, do_sample=False)
    return str(output[0]["generated_text"]).strip()


def explain_concept(topic: str) -> tuple[str, str]:
    topic = topic.strip()
    if not topic:
        raise ValueError("Please enter a topic to explain.")

    if settings.explain_provider == "local":
        return _explain_with_local(topic), settings.local_explain_model

    result = client.generate(
        "Explain this topic for a student:\n\n" + truncate(topic, 6000),
        system_instruction=(
            "You are EduGenie, a patient educational tutor. Explain difficult concepts "
            "clearly without assuming prior knowledge. Use a short definition, key ideas, "
            "and a practical example. Avoid unnecessary jargon."
        ),
        temperature=0.3,
        max_output_tokens=800,
    )
    return result.text, result.model
