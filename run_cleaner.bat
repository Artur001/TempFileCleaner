@echo off
:: TempFileCleaner - Run as Administrator
:: Right-click this file → "Run as administrator" for full cleanup

:: Check for admin privileges and request elevation if needed
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo Requesting administrator privileges...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

cd /d "%~dp0"
python cleaner.py %*
echo.
pause
