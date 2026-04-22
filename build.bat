@echo off
:: Build TempFileCleaner into a standalone .exe
:: Requires: pip install pyinstaller

echo.
echo  Building TempFileCleaner.exe ...
echo.

:: Check if pyinstaller is installed
pyinstaller --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  PyInstaller not found. Installing...
    pip install pyinstaller
    echo.
)

:: Build the exe
pyinstaller ^
    --onefile ^
    --console ^
    --name TempFileCleaner ^
    --icon=NONE ^
    --uac-admin ^
    --clean ^
    cleaner.py

echo.
if exist "dist\TempFileCleaner.exe" (
    echo  ✓ Build successful!
    echo  Output: dist\TempFileCleaner.exe
    echo.
    echo  You can now distribute TempFileCleaner.exe as a standalone file.
    echo  It will auto-request admin privileges when launched.
) else (
    echo  ✗ Build failed. Check the output above for errors.
)

echo.
pause
