@echo off
setlocal
cd /d "%~dp0\.."
if exist ".venv\Scripts\python.exe" (
    set "PYTHON=.venv\Scripts\python.exe"
) else (
    set "PYTHON=python"
)
%PYTHON% -m PyInstaller --clean --noconfirm --distpath dist --workpath build FileFlow.spec
if errorlevel 1 exit /b %errorlevel%
echo.
echo Built dist\FileFlow.exe
