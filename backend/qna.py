"""Question-answering logic."""
from __future__ import annotations

from backend.gemini_client import client
from backend.utils import truncate


def answer_question(question: str, level: str = "beginner") -> tuple[str, str]:
    question = question.strip()
    if not question:
        raise ValueError("Please enter a question.")

    result = client.generate(
        f"Student level: {level}\nQuestion: {truncate(question, 12000)}",
        system_instruction=(
            "You are EduGenie, a helpful academic tutor. Answer the student's question "
            "accurately and concisely. Explain key reasoning when useful. Do not invent "
            "facts; clearly state uncertainty when needed."
        ),
        temperature=0.2,
        max_output_tokens=1000,
    )
    return result.text, result.model
