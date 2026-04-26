@echo off
setlocal
cd /d "%~dp0"

if not exist ".env" (
    echo [LOI] Khong tim thay file .env trong thu muc project.
    pause
    exit /b 1
)

set /p PUBLIC_URL=Dan link https cua ngrok vao day roi nhan Enter: 

if "%PUBLIC_URL%"=="" (
    echo [LOI] Ban chua nhap PUBLIC_URL.
    pause
    exit /b 1
)

set "PUBLIC_URL_INPUT=%PUBLIC_URL%"
powershell -NoProfile -ExecutionPolicy Bypass -Command "$path = '.env'; $publicUrl = $env:PUBLIC_URL_INPUT.Trim(); $content = Get-Content -Raw -Path $path; if ($content -match '(?m)^PUBLIC_URL=.*$') { $content = [regex]::Replace($content, '(?m)^PUBLIC_URL=.*$', ('PUBLIC_URL=' + $publicUrl)) } else { $content = $content.TrimEnd() + [Environment]::NewLine + 'PUBLIC_URL=' + $publicUrl + [Environment]::NewLine }; Set-Content -Path $path -Value $content -Encoding UTF8"

if errorlevel 1 (
    echo [LOI] Khong cap nhat duoc file .env.
    pause
    exit /b 1
)

echo.
echo Da cap nhat PUBLIC_URL=%PUBLIC_URL%
echo Bay gio quay lai web va thanh toan MoMo/VNPAY nhu binh thuong.
pause
