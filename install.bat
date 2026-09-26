@echo off
REM Double-click this file after installing Docker Desktop. It is safe to run again.
setlocal
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\install.ps1"
if errorlevel 1 (
  echo.
  echo Installation did not complete. Read the message above, then run install.bat again.
  pause
  exit /b 1
)
echo.
echo Installation completed. The dashboard should be open in your browser.
pause
