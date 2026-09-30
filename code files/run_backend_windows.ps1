$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

if (-not (Test-Path ".venv\Scripts\python.exe")) {
    Write-Host "Project .venv is missing. Running setup first..." -ForegroundColor Yellow
    & "$PSScriptRoot\setup_backend_windows.ps1"
}

if (-not (Test-Path "backend\.env")) {
    Copy-Item "backend\.env.example" "backend\.env"
}

& ".venv\Scripts\python.exe" -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
