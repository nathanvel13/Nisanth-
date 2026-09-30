@echo off
setlocal
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe call "%~dp0setup_backend_windows.bat"
start "EduGenie Backend" cmd /k "%~dp0run_backend_windows.bat"
timeout /t 2 /nobreak >nul
start "EduGenie Frontend" cmd /k "%~dp0run_frontend_windows.bat"
endlocal
