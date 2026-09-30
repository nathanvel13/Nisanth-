$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "EduGenie backend setup" -ForegroundColor Cyan

$pythonLauncher = Get-Command py -ErrorAction SilentlyContinue
if (-not $pythonLauncher) {
    throw "Python Launcher 'py' was not found. Install Python 3.11 and enable the Python Launcher."
}

$pythonCommand = "py"
$pythonArgs = @("-3.11")
$has311 = & py -3.11 -c "import sys; print(sys.version_info >= (3,10))" 2>$null
if ($LASTEXITCODE -ne 0) { $pythonArgs = @("-3") }

if (Test-Path ".venv") {
    Write-Host "Removing previous .venv ..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force ".venv"
}

& $pythonCommand @pythonArgs -m venv .venv
if ($LASTEXITCODE -ne 0) { throw "Virtual environment creation failed." }

$venvPython = Join-Path (Get-Location) ".venv\Scripts\python.exe"
& $venvPython -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) { throw "pip upgrade failed." }

& $venvPython -m pip install -r "backend\requirements.txt"
if ($LASTEXITCODE -ne 0) { throw "Dependency installation failed. Check your internet connection and try again." }

if (-not (Test-Path "backend\.env")) {
    Copy-Item "backend\.env.example" "backend\.env"
    Write-Host "Created backend/.env. DEMO_MODE=true is enabled for the first run." -ForegroundColor Green
}

Write-Host "Backend setup completed." -ForegroundColor Green
