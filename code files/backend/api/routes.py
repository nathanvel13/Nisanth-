"""FastAPI route definitions for EduGenie."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from backend.config import settings
from backend.explanation_module import explain_concept
from backend.gemini_client import GeminiUnavailableError
from backend.learning_path import get_learning_recommendations
from backend.qna import answer_question
from backend.quiz_module import generate_quiz
from backend.schemas import APIResponse, LearningPathRequest, QARequest, QuizRequest, TextRequest
from backend.summary_module import summarize_text

router = APIRouter(tags=["EduGenie"])


def _demo_text(task: str, text: str) -> str:
    if task == "qa":
        return (
            f"Demo response: I received your question: {text}\n\n"
            "Set DEMO_MODE=false and add GEMINI_API_KEY for live Gemini answers."
        )
    if task == "explain":
        return (
            f"Demo response: The topic you entered is {text}.\n\n"
            "Set DEMO_MODE=false and add GEMINI_API_KEY for a generated explanation."
        )
    if task == "summary":
        return (
            f"Demo summary: {text[:400]}\n\n"
            "Set DEMO_MODE=false and add GEMINI_API_KEY for live summarization."
        )
    return (
        f"Demo learning path for {text}: begin with fundamentals, practice the core skills, "
        "complete a small project, review mistakes, then progress to advanced applications.\n\n"
        "Set DEMO_MODE=false and add GEMINI_API_KEY for a personalized plan."
    )


def _service_error(exc: Exception) -> HTTPException:
    return HTTPException(status_code=503, detail=str(exc))


@router.get("/")
def root() -> dict[str, object]:
    return {
        "app": settings.app_name,
        "status": "ok",
        "service": "backend-api",
        "frontend": "http://127.0.0.1:5500",
        "health": "/health",
        "docs": "/docs",
    }


@router.get("/health")
def health() -> dict[str, object]:
    return {
        "status": "ok",
        "app": settings.app_name,
        "gemini_configured": bool(settings.gemini_api_key),
        "models": settings.gemini_models,
        "explain_provider": settings.explain_provider,
        "demo_mode": settings.demo_mode,
    }


@router.post("/qa", response_model=APIResponse)
def qa(payload: QARequest) -> APIResponse:
    try:
        if settings.demo_mode:
            return APIResponse(result=_demo_text("qa", payload.text), model="demo")
        result, model = answer_question(payload.text, payload.level)
        return APIResponse(result=result, model=model)
    except (ValueError, GeminiUnavailableError) as exc:
        raise _service_error(exc) from exc


@router.post("/explain", response_model=APIResponse)
def explain(payload: TextRequest) -> APIResponse:
    try:
        if settings.demo_mode:
            return APIResponse(result=_demo_text("explain", payload.text), model="demo")
        result, model = explain_concept(payload.text)
        return APIResponse(result=result, model=model)
    except (ValueError, RuntimeError, GeminiUnavailableError) as exc:
        raise _service_error(exc) from exc


@router.post("/summarize", response_model=APIResponse)
def summarize(payload: TextRequest) -> APIResponse:
    try:
        if settings.demo_mode:
            return APIResponse(result=_demo_text("summary", payload.text), model="demo")
        result, model = summarize_text(payload.text)
        return APIResponse(result=result, model=model)
    except (ValueError, GeminiUnavailableError) as exc:
        raise _service_error(exc) from exc


@router.post("/learn/recommendations", response_model=APIResponse)
def learn(payload: LearningPathRequest) -> APIResponse:
    try:
        if settings.demo_mode:
            return APIResponse(result=_demo_text("learn", payload.text), model="demo")
        result, model = get_learning_recommendations(payload.text, payload.level, payload.weeks)
        return APIResponse(result=result, model=model)
    except (ValueError, GeminiUnavailableError) as exc:
        raise _service_error(exc) from exc


@router.post("/quiz")
def quiz(payload: QuizRequest) -> dict[str, object]:
    try:
        if settings.demo_mode:
            questions = []
            for index in range(payload.count):
                options = [
                    f"Option A{index + 1}",
                    f"Option B{index + 1}",
                    f"Option C{index + 1}",
                    f"Option D{index + 1}",
                ]
                questions.append(
                    {
                        "question": f"Demo question {index + 1} about {payload.text[:80]}",
                        "options": options,
                        "correct_answer": options[0],
                        "explanation": "Demo mode. Enable Gemini for generated questions.",
                    }
                )
            return {"success": True, "topic": payload.text[:120], "questions": questions, "model": "demo"}

        quiz_data, model = generate_quiz(payload.text, payload.count)
        return {"success": True, **quiz_data.model_dump(), "model": model}
    except (ValueError, GeminiUnavailableError) as exc:
        raise _service_error(exc) from exc
