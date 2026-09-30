"""Multiple-choice quiz generation and validation."""
from __future__ import annotations

import json

from backend.gemini_client import client
from backend.schemas import QuizResponse
from backend.utils import clean_json_block, truncate

QUIZ_SCHEMA = {
    "type": "object",
    "properties": {
        "topic": {"type": "string"},
        "questions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "question": {"type": "string"},
                    "options": {"type": "array", "items": {"type": "string"}},
                    "correct_answer": {"type": "string"},
                    "explanation": {"type": "string"},
                },
                "required": ["question", "options", "correct_answer", "explanation"],
            },
        },
    },
    "required": ["topic", "questions"],
}


def _validate(payload: object, count: int) -> QuizResponse:
    parsed = QuizResponse.model_validate(payload)
    if len(parsed.questions) < count:
        raise ValueError(f"Model returned {len(parsed.questions)} questions; expected {count}.")
    parsed.questions = parsed.questions[:count]
    for question in parsed.questions:
        if len(question.options) != 4:
            raise ValueError("Every quiz question must contain exactly four options.")
        if len(set(question.options)) != 4:
            raise ValueError("Every quiz question must contain four different options.")
        if question.correct_answer not in question.options:
            raise ValueError("correct_answer must exactly match one of the four options.")
    return parsed


def generate_quiz(source_text: str, count: int = 3) -> tuple[QuizResponse, str]:
    source_text = source_text.strip()
    if not source_text:
        raise ValueError("Please enter a topic or passage for the quiz.")

    prompt = f"""
Create exactly {count} multiple-choice questions from the content below.
Return ONLY JSON matching the requested schema. No Markdown code fences.
Each question must have exactly four different options.
The correct_answer value must exactly match one option.
Include a short explanation for every answer.

CONTENT:
{truncate(source_text, 15000)}
""".strip()

    result = client.generate(
        prompt,
        system_instruction="You are EduGenie's assessment generator. Make clear and fair educational MCQs.",
        temperature=0.25,
        max_output_tokens=3200,
        response_mime_type="application/json",
        response_schema=QUIZ_SCHEMA,
    )

    try:
        payload = json.loads(clean_json_block(result.text))
    except json.JSONDecodeError as exc:
        raise ValueError("Gemini returned invalid quiz JSON. Please retry the quiz.") from exc

    return _validate(payload, count), result.model
