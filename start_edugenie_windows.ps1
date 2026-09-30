$ErrorActionPreference = "Stop"
$root = $PSScriptRoot

if (-not (Test-Path "$root\.venv\Scripts\python.exe")) {
    & "$root\setup_backend_windows.ps1"
}

Start-Process powershell -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-File", "$root\run_backend_windows.ps1"
Start-Sleep -Seconds 2
Start-Process powershell -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-File", "$root\run_frontend_windows.ps1"

Write-Host "Backend and frontend terminals have been started." -ForegroundColor Green
