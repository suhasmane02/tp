# One-click Windows installer for the local-only Docker application.
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
Write-Host "YouTube Vlog Analytics - local installer" -ForegroundColor Cyan

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
  Write-Host "Docker Desktop is required but was not found." -ForegroundColor Red
  Write-Host "Install Docker Desktop from https://www.docker.com/products/docker-desktop/, start it, then double-click install.bat again."
  exit 1
}
try { docker info *> $null } catch {
  Write-Host "Docker Desktop is installed but is not running." -ForegroundColor Red
  Write-Host "Start Docker Desktop, wait until it says 'Engine running', then double-click install.bat again."
  exit 1
}
if (-not (Test-Path .env)) {
  Copy-Item .env.example .env
  # A local random application secret lets the app start safely without asking for credentials.
  $secret = -join ((48..57)+(65..90)+(97..122) | Get-Random -Count 48 | ForEach-Object {[char]$_})
  (Get-Content .env) -replace '^APP_SECRET_KEY=.*$', "APP_SECRET_KEY=$secret" | Set-Content .env -Encoding utf8
  Write-Host "Created .env. Google credentials are optional for demo mode and can be added later." -ForegroundColor Yellow
}
Write-Host "Downloading/building containers. The first run can take several minutes..." -ForegroundColor Cyan
docker compose up -d --build
Write-Host "Waiting for the dashboard..." -ForegroundColor Cyan
$ready = $false
for ($i=0; $i -lt 36; $i++) {
  try {
    $response = Invoke-WebRequest -UseBasicParsing http://localhost:8000/ready -TimeoutSec 3
    if ($response.StatusCode -eq 200) { $ready = $true; break }
  } catch {}
  Start-Sleep -Seconds 5
}
if (-not $ready) {
  Write-Host "The containers started but the dashboard is not ready yet." -ForegroundColor Yellow
  Write-Host "Run logs.bat to see startup logs, then open http://localhost:8000 when ready."
  exit 1
}
Start-Process 'http://localhost:8000'
Write-Host "Ready. The dashboard is available only on this computer at http://localhost:8000" -ForegroundColor Green
