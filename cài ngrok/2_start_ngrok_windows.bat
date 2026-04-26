@echo off
setlocal EnableDelayedExpansion
cd /d "%~dp0"

set "PORT=5011"
set "NGROK_CMD="
set "NGROK_CONFIG=%~dp0ngrok.local.yml"

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

if not exist "%NGROK_CONFIG%" (
    echo ===============================================
    echo Chua co file cau hinh ngrok rieng cho project nay.
    echo Nhap authtoken de tao file %NGROK_CONFIG%
    echo Lay authtoken tai: https://dashboard.ngrok.com/get-started/your-authtoken
    echo ===============================================
    set /p NGROK_TOKEN=Authtoken: 
    if not defined NGROK_TOKEN (
        echo [LOI] Ban chua nhap authtoken.
        pause
        exit /b 1
    )
    "%NGROK_CMD%" config add-authtoken "!NGROK_TOKEN!" --config "%NGROK_CONFIG%"
    if errorlevel 1 (
        echo [LOI] Khong tao duoc file cau hinh ngrok rieng cho project.
        pause
        exit /b 1
    )
    echo.
    echo Da luu authtoken vao %NGROK_CONFIG%
    echo.
)

"%NGROK_CMD%" config check --config "%NGROK_CONFIG%" >nul 2>nul
if errorlevel 1 (
    echo [LOI] File cau hinh ngrok cua project dang loi: %NGROK_CONFIG%
    echo Hay xoa file do roi chay lai script nay de nhap authtoken moi.
    pause
    exit /b 1
)

echo ===============================================
echo Dang mo ngrok cho cong %PORT%
echo Sau khi thay dong Forwarding, copy link https://...ngrok...
echo Roi chay file 3_cap_nhat_public_url_windows.bat
echo ===============================================
echo.

"%NGROK_CMD%" http %PORT% --config "%NGROK_CONFIG%"
pause
