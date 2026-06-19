@echo off
echo === Starting Windows Production Deployment ===

:: 1. Git Pull
if exist .git (
    echo [1/4] Pulling latest code...
    git pull origin main
) else (
    echo [1/4] Skipping git pull (not a git repository).
)

:: 2. Create Venv if missing
if not exist venv (
    echo [2/4] Creating virtual environment...
    python -m venv venv
)

:: 3. Activate Venv and Install dependencies
echo [3/4] Activating venv and installing dependencies...
call venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt

:: 4. Reset & Seed DB
echo [4/4] Resetting and seeding database...
python reset_db.py

echo.
echo [✓] Deployment and database reset complete!
echo Starting Waitress server...
echo.

:: 5. Run the Server
python run_windows.py
pause
