@echo off
:: TempFileCleaner - Dry Run (scan only, nothing gets deleted)

cd /d "%~dp0"
python cleaner.py --dry-run
echo.
pause
