# EduGenie — Google Gemini Powered Learning Assistant

EduGenie is a complete student-focused AI learning assistant reconstructed from the supplied project documentation.

## What is included

- Separate **frontend** and **backend** folders.
- FastAPI backend with the documented endpoints:
  - `POST /qa`
  - `POST /explain`
  - `POST /quiz`
  - `POST /summarize`
  - `POST /learn/recommendations`
- Health and API documentation endpoints:
  - `GET /`
  - `GET /health`
  - `GET /docs`
  - `GET /redoc`
- Google Gemini integration for Q&A, explanations, quizzes, summaries, and learning paths.
- Automatic Gemini model rotation when a model is busy, rate limited, unavailable, invalid for the key, times out, or returns another transient service failure.
- Optional local LaMini-Flan-T5 explanation provider, matching the original document.
- Frontend is plain HTML/CSS/JavaScript, so Node/npm is **not required** for the basic project.
- Frontend is served locally on port `5500` by the included PowerShell script.
- Demo mode lets you verify frontend/backend wiring without a Gemini API key.
- Automated backend tests for validation, all routes, JSON parsing, and model failover.

## Architecture

```text
EduGenie/
├── backend/
│   ├── main.py
│   ├── config.py
│   ├── schemas.py
│   ├── gemini_client.py
│   ├── qna.py
│   ├── explanation_module.py
│   ├── quiz_module.py
│   ├── summary_module.py
│   ├── learning_path.py
│   ├── utils.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── templates/
│   │   └── index.html
│   ├── static/
│   │   └── style.css
│   ├── tests/
│   │   ├── conftest.py
│   │   ├── test_api.py
│   │   ├── test_gemini_client.py
│   │   └── test_utils.py
│   ├── requirements.txt
│   ├── requirements-local.txt
│   └── .env.example
├── frontend/
│   ├── index.html
│   ├── app.js
│   ├── style.css
│   ├── config.js
│   └── README.md
├── setup_backend_windows.ps1
├── run_backend_windows.ps1
├── run_frontend_windows.ps1
└── .gitignore
```

## 1. Requirements

Recommended for the least friction:

- Windows 10/11
- Python 3.11
- A modern browser
- Internet connection when installing packages and when using live Gemini
- A Google Gemini API key for live AI mode

The official `google-genai` SDK supports Python 3.10+.

## 2. IMPORTANT: do not reuse an old virtual environment

The project is designed to create its virtual environment at:

```text
EduGenie/\.venv
```

Do **not** install backend packages into an unrelated/root `.venv` created for another project.

### Easiest Windows setup

Open PowerShell in the **EduGenie project root** and run:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
.\setup_backend_windows.ps1
```

The setup script removes the old `\.venv` if needed, creates a clean one, upgrades pip, installs the exact tested package versions, and creates `backend/.env` from the example file.

## 3. Backend setup manually

From the project root:

```powershell
cd backend
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r backend\requirements.txt
Copy-Item .env.example .env
```

Edit `backend/.env`.

For the safest first run, keep:

```text
DEMO_MODE=true
```

This confirms the complete frontend -> backend -> API flow before you add a key.

For live Gemini:

```text
DEMO_MODE=false
GEMINI_API_KEY=YOUR_GEMINI_API_KEY
```

Never commit a real API key to Git.

## 4. Start the backend

From `EduGenie/backend`:

```powershell
.\.venv\Scripts\python.exe -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

You should see:

```text
Uvicorn running on http://127.0.0.1:8000
```

Check:

- `http://127.0.0.1:8000/health`
- `http://127.0.0.1:8000/docs`

## 5. Start the frontend

Keep the backend terminal running. Open a second terminal in the project root and run:

```powershell
.\run_frontend_windows.ps1
```

The script serves the `frontend/` directory with Python's built-in web server on:

```text
http://127.0.0.1:5500
```

Open that address in the browser.

No npm install is required for the included frontend.

## 6. API payloads

### Q&A

`POST /qa`

```json
{
  "text": "Which is the largest ocean?",
  "level": "beginner"
}
```

### Explanation

`POST /explain`

```json
{
  "text": "Explain the Pythagorean theorem"
}
```

### Quiz

`POST /quiz`

```json
{
  "text": "The water cycle is the continuous movement of water...",
  "count": 3
}
```

### Summary

`POST /summarize`

```json
{
  "text": "Paste the educational passage here..."
}
```

### Learning path

`POST /learn/recommendations`

```json
{
  "text": "SQL",
  "level": "beginner",
  "weeks": 6
}
```

## 7. Model failover

EduGenie reads `GEMINI_MODELS` from `.env` and tries them in order.

Default list:

```text
gemini-3.8-flash
gemini-3.7-flash
gemini-3.6-flash
gemini-3.5-flash
gemini-3.5-flash-lite
```

The client treats common transient failures as failover candidates, including:

- HTTP 408
- HTTP 429
- HTTP 500/502/503/504
- resource exhausted / rate-limit errors
- unavailable / overloaded / busy / capacity messages
- timeouts and connection resets

A retry is attempted according to `GEMINI_ATTEMPTS_PER_MODEL`; then the next model is tried. The successful model is returned in the API response.

## 8. Optional LaMini-Flan-T5 provider

The original project document names LaMini-Flan-T5-783M as a local explanation model.

The default project uses Gemini for explanations so the standard installation stays lightweight.

To enable the optional local provider:

```powershell
cd backend
.\.venv\Scripts\python.exe -m pip install -r requirements-local.txt
```

Then set:

```text
EXPLAIN_PROVIDER=local
LOCAL_EXPLAIN_MODEL=MBZUAI/LaMini-Flan-T5-783M
```

The model download can be large and requires access to the model host. The normal Gemini provider does not require this local model.

## 9. Run tests

From `EduGenie/backend`:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

The tests do not make live Gemini calls. They verify the API contracts and simulate model failures/successes so that failover can be tested without using your API quota.

## 10. Common Windows errors

### `uvicorn is not recognized`

Do not run the global `uvicorn` executable. Run:

```powershell
.\.venv\Scripts\python.exe -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

### `ResolutionImpossible`

You are probably reusing an old virtual environment. From the project root run:

```powershell
.\setup_backend_windows.ps1
```

The script uses the project-local `\.venv` and the tested requirements file.

### Frontend says `Backend unavailable`

Make sure the backend terminal is still running on port 8000 before opening the frontend.

### Gemini returns an error

First set `DEMO_MODE=true` and verify the application. Then set `DEMO_MODE=false`, add `GEMINI_API_KEY`, restart the backend, and try again. If one Gemini model is busy or rate limited, the backend rotates through the configured fallback models.

## 11. What this package does not guarantee

No software can guarantee that an external AI service will always be available. EduGenie minimizes this risk with model rotation and retries. Live Gemini usage still depends on your API key, account access, quota, network connection, and Google's service availability.

## 12. Even easier Windows launch

You can also double-click these batch files from the project folder:

- `setup_backend_windows.bat` — creates the clean backend environment and installs dependencies.
- `run_backend_windows.bat` — starts FastAPI.
- `run_frontend_windows.bat` — starts the separate frontend server.
- `start_edugenie_windows.bat` — opens backend and frontend in separate terminal windows.
