@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    echo Run setup.ps1 first. See README.md for setup instructions.
    exit /b 1
)
call ".venv\Scripts\activate.bat"
python scripts\preflight.py
if errorlevel 1 exit /b 1
python -m jupyterlab
endlocal
