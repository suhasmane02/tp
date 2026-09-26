@echo off
setlocal
if not exist .env (
  call "%~dp0install.bat"
  exit /b %errorlevel%
)
docker compose up -d
timeout /t 3 /nobreak >nul
start "" http://localhost:8000
