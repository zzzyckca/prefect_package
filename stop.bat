@echo off
setlocal

echo ===================================================
echo   Prefect 3.x System Shutdown                      
echo ===================================================
echo.

echo [Step 1/1] Stopping Prefect background processes...
taskkill /F /IM prefect.exe /T >nul 2>&1

echo.
echo ===================================================
echo   Prefect successfully stopped.                    
echo ===================================================
pause
