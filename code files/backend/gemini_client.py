"""Resilient Google Gemini client with automatic model rotation."""
from __future__ import annotations

import logging
import random
import time
from dataclasses import dataclass
from typing import Any

from backend.config import settings

logger = logging.getLogger(__name__)

try:
    from google import genai
    from google.genai import types
except ImportError:  # pragma: no cover - runtime dependency checked when live mode is used
    genai = None  # type: ignore[assignment]
    types = None  # type: ignore[assignment]


class GeminiUnavailableError(RuntimeError):
    """Raised when no configured Gemini model produces a usable response."""


@dataclass(frozen=True)
class GenerationResult:
    text: str
    model: str
    attempts: int


class GeminiClient:
    def __init__(self) -> None:
        self.api_key = settings.gemini_api_key
        self.models = list(settings.gemini_models)
        self.attempts_per_model = max(1, settings.gemini_attempts_per_model)
        self.backoff_seconds = max(0.0, settings.gemini_backoff_seconds)
        self.timeout_seconds = max(5.0, settings.gemini_timeout_seconds)
        self._client: Any | None = None

    @property
    def configured(self) -> bool:
        return bool(self.api_key) and genai is not None

    def _get_client(self) -> Any:
        if self._client is not None:
            return self._client
        if not self.api_key:
            raise GeminiUnavailableError(
                "GEMINI_API_KEY is missing. Add it to backend/.env and restart the backend."
            )
        if genai is None or types is None:
            raise GeminiUnavailableError(
                "The google-genai package is not installed. Run: python -m pip install -r requirements.txt"
            )
        self._client = genai.Client(
            api_key=self.api_key,
            http_options=types.HttpOptions(timeout=int(self.timeout_seconds * 1000)),
        )
        return self._client

    @staticmethod
    def _error_text(exc: Exception) -> str:
        parts = [str(exc)]
        for attr in ("message", "status_code", "code"):
            value = getattr(exc, attr, None)
            if value is not None:
                parts.append(str(value))
        return " | ".join(dict.fromkeys(part for part in parts if part))

    @classmethod
    def _is_retryable(cls, exc: Exception) -> bool:
        message = cls._error_text(exc).lower()
        retry_markers = (
            "408", "409", "425", "429", "500", "502", "503", "504", "529",
            "resource_exhausted", "resource exhausted", "rate limit", "rate_limited",
            "unavailable", "overloaded", "capacity", "busy", "temporarily",
            "timeout", "timed out", "deadline", "connection reset", "connection aborted",
            "internal error", "server error", "quota",
        )
        return any(marker in message for marker in retry_markers)

    def generate(
        self,
        prompt: str,
        *,
        system_instruction: str | None = None,
        temperature: float = 0.4,
        max_output_tokens: int = 1200,
        response_mime_type: str | None = None,
        response_schema: Any | None = None,
    ) -> GenerationResult:
        if not self.models:
            raise GeminiUnavailableError("No Gemini models are configured in GEMINI_MODELS.")

        client = self._get_client()
        failures: list[str] = []
        total_attempts = 0

        for model in self.models:
            for attempt in range(self.attempts_per_model):
                total_attempts += 1
                try:
                    if types is None:
                        raise GeminiUnavailableError("Google Gen AI types are unavailable.")

                    config_kwargs: dict[str, Any] = {
                        "temperature": temperature,
                        "max_output_tokens": max_output_tokens,
                    }
                    if system_instruction:
                        config_kwargs["system_instruction"] = system_instruction
                    if response_mime_type:
                        config_kwargs["response_mime_type"] = response_mime_type
                    if response_schema is not None:
                        config_kwargs["response_schema"] = response_schema

                    response = client.models.generate_content(
                        model=model,
                        contents=prompt,
                        config=types.GenerateContentConfig(**config_kwargs),
                    )
                    text = (getattr(response, "text", "") or "").strip()
                    if not text:
                        raise GeminiUnavailableError(f"Model {model} returned an empty response.")
                    logger.info("Gemini success model=%s attempt=%s", model, attempt + 1)
                    return GenerationResult(text=text, model=model, attempts=total_attempts)
                except Exception as exc:
                    error_text = self._error_text(exc)
                    failures.append(f"{model}: {error_text}")
                    retryable = self._is_retryable(exc)
                    logger.warning(
                        "Gemini failure model=%s attempt=%s retryable=%s error=%s",
                        model,
                        attempt + 1,
                        retryable,
                        error_text,
                    )

                    # Always move to the next configured model after a failed model.
                    # Retry the same model first only when the error is clearly transient.
                    if retryable and attempt + 1 < self.attempts_per_model:
                        delay = self.backoff_seconds * (2**attempt) + random.uniform(0.0, 0.25)
                        if delay > 0:
                            time.sleep(delay)
                    else:
                        break

        detail = " | ".join(failures[-8:])
        raise GeminiUnavailableError(
            "All configured Gemini models failed. EduGenie automatically rotated through "
            f"{len(self.models)} configured model(s). Details: {detail}"
        )


client = GeminiClient()
