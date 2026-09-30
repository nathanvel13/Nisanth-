@echo off
setlocal
cd /d "%~dp0"
echo EduGenie backend setup
py -3.11 -m venv .venv
if errorlevel 1 (
  echo Python 3.11 not found. Trying default Python...
  py -3 -m venv .venv
  if errorlevel 1 exit /b 1
)
.venv\Scripts\python.exe -m pip install --upgrade pip
if errorlevel 1 exit /b 1
.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
if errorlevel 1 exit /b 1
if not exist backend\.env copy backend\.env.example backend\.env >nul
echo Setup complete.
endlocal
