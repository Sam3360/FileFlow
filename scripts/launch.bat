@echo off
setlocal
cd /d "%~dp0\.."
if exist ".venv\Scripts\python.exe" (
    call ".venv\Scripts\activate.bat"
    python -m fileflow
) else (
    echo FileFlow environment not found.
    echo Run setup.bat first.
    pause
)
