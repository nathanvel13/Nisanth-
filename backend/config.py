"""Environment-backed settings for EduGenie."""
from __future__ import annotations

import os
from pathlib import Path
from dataclasses import dataclass, field

from dotenv import load_dotenv

load_dotenv(Path(__file__).with_name(".env"))

DEFAULT_GEMINI_MODELS = [
    "gemini-3.8-flash",
    "gemini-3.7-flash",
    "gemini-3.6-flash",
    "gemini-3.5-flash",
    "gemini-3.5-flash-lite",
]


def _csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def _bool(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def _int(value: str, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _float(value: str, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


@dataclass(frozen=True)
class Settings:
    app_name: str = field(default_factory=lambda: os.getenv("APP_NAME", "EduGenie").strip() or "EduGenie")
    host: str = field(default_factory=lambda: os.getenv("HOST", "127.0.0.1").strip() or "127.0.0.1")
    port: int = field(default_factory=lambda: _int(os.getenv("PORT", "8000"), 8000))
    debug: bool = field(default_factory=lambda: _bool(os.getenv("DEBUG", "true")))
    gemini_api_key: str = field(default_factory=lambda: os.getenv("GEMINI_API_KEY", "").strip())
    gemini_models: list[str] = field(default_factory=lambda: _csv(os.getenv("GEMINI_MODELS", ",".join(DEFAULT_GEMINI_MODELS))) or DEFAULT_GEMINI_MODELS.copy())
    gemini_attempts_per_model: int = field(default_factory=lambda: max(1, _int(os.getenv("GEMINI_ATTEMPTS_PER_MODEL", "1"), 1)))
    gemini_backoff_seconds: float = field(default_factory=lambda: max(0.0, _float(os.getenv("GEMINI_BACKOFF_SECONDS", "1.0"), 1.0)))
    gemini_timeout_seconds: float = field(default_factory=lambda: max(5.0, _float(os.getenv("GEMINI_TIMEOUT_SECONDS", "45"), 45.0)))
    explain_provider: str = field(default_factory=lambda: os.getenv("EXPLAIN_PROVIDER", "gemini").strip().lower() or "gemini")
    local_explain_model: str = field(default_factory=lambda: os.getenv("LOCAL_EXPLAIN_MODEL", "MBZUAI/LaMini-Flan-T5-783M").strip())
    demo_mode: bool = field(default_factory=lambda: _bool(os.getenv("DEMO_MODE", "true")))
    cors_origins: list[str] = field(default_factory=lambda: _csv(os.getenv("CORS_ORIGINS", "http://127.0.0.1:5500,http://localhost:5500,http://127.0.0.1:5173,http://localhost:5173")))


settings = Settings()
