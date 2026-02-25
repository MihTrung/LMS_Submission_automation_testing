@echo off
echo.
echo ===========================================
echo   LMS Automation Setup (Python Playwright)
echo ===========================================
echo.

IF NOT EXIST venv (
    echo [1/3] Creating virtual environment...
    python -m venv venv
) ELSE (
    echo [1/3] Virtual environment already exists.
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
