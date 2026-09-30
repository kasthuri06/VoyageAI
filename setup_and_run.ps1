# ============================================================
#  Voyage AI — Automated Setup & Run Script (Windows)
#  Run from the VoyageAI/ directory:
#    cd VoyageAI
#    powershell -ExecutionPolicy Bypass -File setup_and_run.ps1
# ============================================================

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Voyage AI - Setup & Run Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$rootDir    = $PSScriptRoot
$backendDir = Join-Path $rootDir "backend"
$frontendDir= Join-Path $rootDir "frontend"

# ── Step 1: Backend virtual environment ─────────────────────
Write-Host "[1/6] Setting up Python virtual environment..." -ForegroundColor Yellow

Set-Location $backendDir

if (-not (Test-Path "venv")) {
    python -m venv venv
    Write-Host "      Virtual environment created." -ForegroundColor Green
} else {
    Write-Host "      Virtual environment already exists." -ForegroundColor Green
}

# ── Step 2: Install Python packages ─────────────────────────
Write-Host "[2/6] Installing Python dependencies..." -ForegroundColor Yellow
& "venv\Scripts\pip.exe" install -r requirements.txt --quiet
Write-Host "      Python packages installed." -ForegroundColor Green

# ── Step 3: Train ML model ───────────────────────────────────
Write-Host "[3/6] Training ML recommendation model..." -ForegroundColor Yellow
& "venv\Scripts\python.exe" ml/train_model.py
Write-Host "      Model trained and saved." -ForegroundColor Green

# ── Step 4: Frontend install ─────────────────────────────────
Write-Host "[4/6] Installing frontend dependencies..." -ForegroundColor Yellow
Set-Location $frontendDir
npm install --silent
Write-Host "      npm packages installed." -ForegroundColor Green

# ── Step 5: Start backend ────────────────────────────────────
Write-Host "[5/6] Starting FastAPI backend on http://localhost:8000 ..." -ForegroundColor Yellow
Set-Location $backendDir
Start-Process powershell -ArgumentList "-NoExit", "-Command", `
    "Set-Location '$backendDir'; venv\Scripts\uvicorn.exe main:app --reload --port 8000" `
    -WindowStyle Normal

Start-Sleep -Seconds 3

# ── Step 6: Start frontend ───────────────────────────────────
Write-Host "[6/6] Starting React frontend on http://localhost:5173 ..." -ForegroundColor Yellow
Set-Location $frontendDir
Start-Process powershell -ArgumentList "-NoExit", "-Command", `
    "Set-Location '$frontendDir'; npm run dev" `
    -WindowStyle Normal

Start-Sleep -Seconds 2

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Voyage AI is running!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "  Frontend  ->  http://localhost:5173" -ForegroundColor Cyan
Write-Host "  API Docs  ->  http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "  NOTE: No PostgreSQL detected." -ForegroundColor Yellow
Write-Host "  The app runs in CSV-only mode (no user accounts)." -ForegroundColor Yellow
Write-Host "  To enable login/save trips, see README for DB setup." -ForegroundColor Yellow
Write-Host ""

Set-Location $rootDir
