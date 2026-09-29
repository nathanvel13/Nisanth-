from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from models import (
    GenerateRequest,
    QuizResponse,
    LearningPathResponse,
    TextResponse,
)

from qna import answer_question
from explanation_module import explain_topic
from quiz_module import generate_quiz
from summary_module import summarize_text
from learning_path import get_learning_recommendations


BASE_DIR = Path(__file__).resolve().parent


app = FastAPI(
    title="EduGenie",
    description="Google Gemini Powered Learning Assistant",
    version="1.0.0",
)


# Static files
app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR / "static"),
    name="static",
)


# Templates
templates = Jinja2Templates(
    directory=str(BASE_DIR / "templates")
)


# ---------------------------------------------------------
# HOME
# ---------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request
        }
    )


# ---------------------------------------------------------
# HEALTH CHECK
# ---------------------------------------------------------

@app.get("/health")
async def health():

    return {
        "status": "ok",
        "service": "EduGenie"
    }


# ---------------------------------------------------------
# QUESTION ANSWERING
# ---------------------------------------------------------

@app.post("/qa", response_model=TextResponse)
async def qa(payload: GenerateRequest):

    try:

        result = answer_question(
            payload.text
        )

        return TextResponse(
            result=result
        )

    except Exception as exc:

        raise HTTPException(
            status_code=502,
            detail=str(exc)
        )


# ---------------------------------------------------------
# EXPLANATION
# ---------------------------------------------------------

@app.post("/explain", response_model=TextResponse)
async def explain(payload: GenerateRequest):

    try:

        result = explain_topic(
            payload.text
        )

        return TextResponse(
            result=result
        )

    except Exception as exc:

        raise HTTPException(
            status_code=502,
            detail=str(exc)
        )


# ---------------------------------------------------------
# QUIZ
# ---------------------------------------------------------

@app.post("/quiz", response_model=QuizResponse)
async def quiz(payload: GenerateRequest):

    try:

        return generate_quiz(
            payload.text
        )

    except Exception as exc:

        raise HTTPException(
            status_code=502,
            detail=str(exc)
        )


# ---------------------------------------------------------
# SUMMARY
# ---------------------------------------------------------

@app.post("/summarize", response_model=TextResponse)
async def summarize(payload: GenerateRequest):

    try:

        result = summarize_text(
            payload.text
        )

        return TextResponse(
            result=result
        )

    except Exception as exc:

        raise HTTPException(
            status_code=502,
            detail=str(exc)
        )


# ---------------------------------------------------------
# LEARNING PATH
# ---------------------------------------------------------

@app.post(
    "/learn/recommendations",
    response_model=LearningPathResponse
)
async def recommendations(
    payload: GenerateRequest
):

    try:

        return get_learning_recommendations(
            payload.text
        )

    except Exception as exc:

        raise HTTPException(
            status_code=502,
            detail=str(exc)
        )