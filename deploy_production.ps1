$ErrorActionPreference = "Stop"

Write-Host "=== Starting Windows Production Deployment ===" -ForegroundColor Cyan

# 1. Pull latest code from git if applicable
if (Test-Path ".git") {
    Write-Host "[1/4] Pulling latest code..." -ForegroundColor Yellow
    git pull origin main
} else {
    Write-Host "[1/4] Skipping git pull (not a git repository)." -ForegroundColor DarkGray
}

# 2. Set up / Activate Virtual Environment
Write-Host "[2/4] Setting up Python virtual environment..." -ForegroundColor Yellow
if (-not (Test-Path "venv")) {
    python -m venv venv
}
& .\venv\Scripts\Activate.ps1

# 3. Upgrade Pip & Install Dependencies
Write-Host "[3/4] Installing dependencies..." -ForegroundColor Yellow
python -m pip install --upgrade pip
pip install -r requirements.txt

# 4. Wipe & Reset Database
Write-Host "[4/4] Resetting and seeding database..." -ForegroundColor Yellow
python reset_db.py

Write-Host "`n[✓] Deployment and database reset complete!" -ForegroundColor Green
Write-Host "Starting Waitress server on http://localhost:8000 ...`n" -ForegroundColor Cyan

# 5. Run Waitress WSGI Server
python run_windows.py
