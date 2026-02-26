@echo off
echo.
echo ===========================================
echo   LMS Automation Setup (Python Playwright)
echo ===========================================
echo.

SET RECREATE=0
IF EXIST venv (
    venv\Scripts\python.exe --version >nul 2>&1
    IF ERRORLEVEL 1 (
        echo [1/3] Virtual environment detected as broken.
        SET RECREATE=1
    )
)

IF "%RECREATE%"=="1" (
    echo Re-creating venv...
    rmdir /s /q venv
)

IF NOT EXIST venv (
    echo [1/3] Creating virtual environment...
    python -m venv venv
) ELSE (
    echo [1/3] Virtual environment already exists and is healthy.
)

echo [2/3] Installing dependencies...
call venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt

echo [3/3] Installing Playwright browsers...
playwright install

echo.
echo Setup complete! To run tests, use: 
echo pytest
echo.
pause
