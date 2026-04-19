@echo off
setlocal
cd /d "%~dp0"

set "PORT=5011"
set "NGROK_CMD="

if exist "ngrok.exe" (
    set "NGROK_CMD=%~dp0ngrok.exe"
) else (
    where ngrok >nul 2>nul
    if not errorlevel 1 set "NGROK_CMD=ngrok"
)

if not defined NGROK_CMD (
    echo [LOI] Khong tim thay ngrok.exe.
    echo Cach de nhat: copy file ngrok.exe vao cung thu muc voi project nay.
    pause
    exit /b 1
)

echo ===============================================
echo Dang mo ngrok cho cong %PORT%
echo Sau khi thay dong Forwarding, copy link https://...ngrok...
echo Roi chay file 3_cap_nhat_public_url_windows.bat
echo ===============================================
echo.

"%NGROK_CMD%" http %PORT%
pause
