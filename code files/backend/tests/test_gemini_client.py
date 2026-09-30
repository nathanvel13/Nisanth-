from dataclasses import dataclass

import backend.gemini_client as gemini_client
from backend.gemini_client import GeminiClient, GeminiUnavailableError


@dataclass
class FakeResponse:
    text: str


class FakeModels:
    def __init__(self):
        self.calls = []

    def generate_content(self, *, model, contents, config):
        self.calls.append(model)
        if model == "busy-model":
            raise RuntimeError("503 model busy")
        return FakeResponse("hello from fallback")


class FakeClient:
    def __init__(self):
        self.models = FakeModels()


def test_model_rotation_after_503(monkeypatch):
    fake = FakeClient()
    client = GeminiClient()
    client.api_key = "test"
    client.models = ["busy-model", "working-model"]
    client.attempts_per_model = 1
    monkeypatch.setattr(client, "_get_client", lambda: fake)
    monkeypatch.setattr(gemini_client, "types", type("T", (), {
        "GenerateContentConfig": lambda **kwargs: kwargs,
    }))

    result = client.generate("hello")
    assert result.model == "working-model"
    assert fake.models.calls == ["busy-model", "working-model"]


def test_missing_key_is_explicit(monkeypatch):
    client = GeminiClient()
    client.api_key = ""
    client.models = ["working-model"]
    client._client = None
    monkeypatch.setattr(gemini_client, "genai", object())
    try:
        client.generate("hello")
    except GeminiUnavailableError as exc:
        assert "GEMINI_API_KEY" in str(exc)
    else:
        raise AssertionError("Expected GeminiUnavailableError")
