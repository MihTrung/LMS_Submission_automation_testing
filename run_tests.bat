@echo off
SETLOCAL

:: Check if venv exists
if not exist "venv\Scripts\activate" (
    echo ERROR: Virtual environment not found. Please run setup.bat first.
    pause
    exit /b 1
)

echo Starting LMS Automation Test Suite...
echo -------------------------------------

:: Run all tests across all configured browsers (defined in pytest.ini)
:: Use 'python -m pytest' to avoid hardcoded paths in the launcher executable
call .\venv\Scripts\python.exe -m pytest code/tests/test_assignment_submission.py %*

echo -------------------------------------
echo Testing Complete.
pause
ENDLOCAL
