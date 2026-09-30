@echo off
setlocal
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe (
  echo Project .venv is missing. Running setup...
  call "%~dp0setup_backend_windows.bat"
  if errorlevel 1 exit /b 1
)
if not exist backend\.env copy backend\.env.example backend\.env >nul
echo EduGenie backend: http://127.0.0.1:8000
echo Swagger:         http://127.0.0.1:8000/docs
.venv\Scripts\python.exe -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
