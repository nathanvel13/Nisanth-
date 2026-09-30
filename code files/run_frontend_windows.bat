@echo off
setlocal
cd /d "%~dp0frontend"
echo EduGenie frontend: http://127.0.0.1:5500
echo Keep the backend running at http://127.0.0.1:8000
echo.
py -3 -m http.server 5500 --bind 127.0.0.1
