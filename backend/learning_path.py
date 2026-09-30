"""Personalized learning-path generation."""
from __future__ import annotations

from backend.gemini_client import client
from backend.utils import truncate


def get_learning_recommendations(topic: str, level: str = "beginner", weeks: int = 6) -> tuple[str, str]:
    topic = topic.strip()
    if not topic:
        raise ValueError("Please enter a topic for the learning path.")

    prompt = f"""
Create a practical {weeks}-week learning path for: {truncate(topic, 5000)}
Learner level: {level}

For every week include:
- goal
- topics
- practice activity
- checkpoint

Also include resource types (documentation, videos, articles, books, or practice sites).
Do not invent direct URLs. Progress from fundamentals to advanced applications.
""".strip()

    result = client.generate(
        prompt,
        system_instruction=(
            "You are EduGenie, an educational learning-path designer. Make the plan realistic, "
            "structured, and suitable for the specified learner level."
        ),
        temperature=0.4,
        max_output_tokens=1800,
    )
    return result.text, result.model
