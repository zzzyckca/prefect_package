@echo off
setlocal

cd /d "%~dp0"

echo ===================================================
echo   Prefect 3.x System Start                         
echo ===================================================
echo.

echo [Step 1/4] Reading config.ini...
for /f "tokens=1,2 delims==" %%A in ('findstr "=" config.ini') do (
    set "%%A=%%B"
)

set "PREFECT_HOME=%PREFECT_HOME%"
set "PREFECT_API_URL=http://127.0.0.1:4200/api"

echo [Step 2/4] Creating hidden VBScript to launch processes...
set "VBS_FILE=%TEMP%\hidden_launcher.vbs"
echo Set WshShell = CreateObject("WScript.Shell") > "%VBS_FILE%"
echo WshShell.Run wscript.Arguments(0), 0, False >> "%VBS_FILE%"

echo [Step 3/4] Starting Prefect Server invisibly in background...
cscript //nologo "%VBS_FILE%" "cmd /c call """%VENV_DIR%\Scripts\activate.bat""" && prefect server start"

timeout /t 10 /nobreak >nul

echo [Step 4/4] Starting Prefect Worker invisibly in background...
cscript //nologo "%VBS_FILE%" "cmd /c call """%VENV_DIR%\Scripts\activate.bat""" && prefect worker start --pool %WORK_POOL_NAME%"

echo.
echo ===================================================
echo   System Online!                                   
echo   Background processes successfully launched. 
echo   You can use stop.bat to terminate them safely.
echo ===================================================
pause
