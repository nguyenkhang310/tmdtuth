@echo off
setlocal
cd /d "%~dp0"

set "PORT=5011"
set "PYTHON_EXE="
set "USE_PY_LAUNCHER=0"

if exist "venv\Scripts\python.exe" (
    set "PYTHON_EXE=venv\Scripts\python.exe"
) else (
    where python >nul 2>nul
    if not errorlevel 1 (
        set "PYTHON_EXE=python"
    ) else (
        where py >nul 2>nul
        if not errorlevel 1 set "USE_PY_LAUNCHER=1"
    )
)

if not defined PYTHON_EXE if "%USE_PY_LAUNCHER%"=="0" (
    echo [LOI] Khong tim thay Python. Hay cai Python hoac tao venv truoc.
    pause
    exit /b 1
)

echo ===============================================
echo Dang chay UTH Store tai http://127.0.0.1:%PORT%
echo Mo file 2_start_ngrok_windows.bat o cua so khac neu can MoMo/VNPAY
echo ===============================================
echo.

if "%USE_PY_LAUNCHER%"=="1" (
    py -3 app.py
) else (
    "%PYTHON_EXE%" app.py
)
pause
