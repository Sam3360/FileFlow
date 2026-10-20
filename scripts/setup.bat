@echo off
setlocal
cd /d "%~dp0\.."
py -3 -m venv .venv
call ".venv\Scripts\activate.bat"
python -m pip install --upgrade pip
python -m pip install -e .
python -m fileflow
