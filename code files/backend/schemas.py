"""Pydantic request and response models used by the API."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator


_LEVELS = {"beginner", "intermediate", "advanced"}


class TextRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=20000)

    @field_validator("text")
    @classmethod
    def non_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Text cannot be blank.")
        return value


class QuizRequest(TextRequest):
    count: int = Field(default=3, ge=1, le=10)


class QARequest(TextRequest):
    level: Literal["beginner", "intermediate", "advanced"] = "beginner"


class LearningPathRequest(TextRequest):
    level: Literal["beginner", "intermediate", "advanced"] = "beginner"
    weeks: int = Field(default=6, ge=1, le=24)


class QuizQuestion(BaseModel):
    question: str = Field(min_length=1)
    options: list[str] = Field(min_length=4, max_length=4)
    correct_answer: str = Field(min_length=1)
    explanation: str = ""


class QuizResponse(BaseModel):
    topic: str = ""
    questions: list[QuizQuestion]


class APIResponse(BaseModel):
    success: bool = True
    result: str | None = None
    model: str | None = None
    error: str | None = None
