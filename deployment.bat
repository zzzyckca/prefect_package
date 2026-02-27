@echo off
setlocal

cd /d "%~dp0"

echo ===================================================
echo   Prefect 3.x Deployment Publisher                 
echo ===================================================
echo.

echo [Step 1/4] Reading config.ini...
for /f "tokens=1,2 delims==" %%A in ('findstr "=" config.ini') do (
    set "%%A=%%B"
)

set "PREFECT_HOME=%PREFECT_HOME%"
set "PREFECT_API_URL=http://127.0.0.1:4200/api"

echo [Step 2/4] Activating virtual environment...
call "%VENV_DIR%\Scripts\activate.bat"

echo [Step 3/4] Ensuring Work Pool '%WORK_POOL_NAME%' exists...
prefect work-pool create "%WORK_POOL_NAME%" --type process >nul 2>&1

echo [Step 4/4] Deploying all flows from prefect.yaml...
prefect deploy --all

echo.
echo ===================================================
echo   Deployment Complete!                             
echo   Jobs are now registered to the Prefect Server.   
echo ===================================================
pause
