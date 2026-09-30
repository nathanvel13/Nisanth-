$ErrorActionPreference = "Stop"
Set-Location "$PSScriptRoot/frontend"
Write-Host "EduGenie frontend: http://127.0.0.1:5500" -ForegroundColor Green
Write-Host "Keep the backend running at http://127.0.0.1:8000" -ForegroundColor Cyan
& py -3 -m http.server 5500 --bind 127.0.0.1
