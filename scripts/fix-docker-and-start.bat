@echo off
:: Self-elevate to admin if not already
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo Requesting Administrator privileges...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

echo ======================================
echo Docker Desktop Registry Fix + Startup
echo ======================================
echo.

:: Add missing AppPath registry value
reg add "HKLM\SOFTWARE\Docker Inc.\Docker Desktop" /v AppPath /t REG_SZ /d "C:\Program Files\Docker\Docker" /f
if %errorlevel% equ 0 (
    echo [OK] AppPath registry value created
) else (
    echo [FAIL] Could not create AppPath registry value
)

:: Verify all values
echo.
echo Registry values:
reg query "HKLM\SOFTWARE\Docker Inc.\Docker Desktop"

:: Start Docker Desktop
echo.
echo Starting Docker Desktop...
start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"
echo.
echo Docker Desktop is launching. Wait 60-90 seconds.
echo Then open a new terminal and run: docker info
echo.
pause
