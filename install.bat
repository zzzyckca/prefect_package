@echo off
setlocal

cd /d "%~dp0"

echo ===================================================
echo   Prefect 3.x Windows Installer                    
echo ===================================================
echo.

echo [Step 1/5] Reading package config.ini...
for /f "tokens=1,2 delims==" %%A in ('findstr "=" config.ini') do (
    set "%%A=%%B"
)

echo [Step 2/5] Creating and copying to target directory %PREFECT_DIR%...
if not exist "%PREFECT_DIR%" (
    mkdir "%PREFECT_DIR%"
)
copy /Y "%~dp0*.*" "%PREFECT_DIR%\" >nul 2>&1

echo [Step 3/5] Shifting context to operational directory...
cd /d "%PREFECT_DIR%"
echo     VENV_DIR        = %VENV_DIR%
echo     PYTHON_PATH     = %PYTHON_PATH%
echo     PIP_CONFIG_FILE = %PIP_CONFIG_FILE%

echo.
echo [Step 4/5] Creating virtual environment...
"%PYTHON_PATH%" -m venv "%VENV_DIR%"
call "%VENV_DIR%\Scripts\activate.bat"

echo.
echo [Step 5/5] Installing dependencies...
pip install -r requirements.txt

echo.
echo ===================================================
echo   Installation Complete!                           
echo   The system is fully operational at %PREFECT_DIR% 
echo ===================================================
pause
