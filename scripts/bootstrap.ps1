# Forge Chamber Bootstrap — Windows PowerShell
# Run: .\scripts\bootstrap.ps1

$ErrorActionPreference = "Stop"

Write-Host "=== Forge Chamber Bootstrap ===" -ForegroundColor Cyan
Write-Host ""

# Check prerequisites
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: python not found. Install Python 3.11.9 from python.org." -ForegroundColor Red
    exit 1
}
if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: node not found. Install Node.js 20 LTS from nodejs.org." -ForegroundColor Red
    exit 1
}

$pythonVersion = python --version 2>&1
$nodeVersion = node --version
Write-Host "Python: $pythonVersion"
Write-Host "Node:   $nodeVersion"
Write-Host ""

# Backend — Python virtual environment + dependencies
Write-Host "[1/4] Setting up Python backend..." -ForegroundColor Yellow
Push-Location backend
python -m venv .venv
& .\.venv\Scripts\Activate.ps1
pip install --upgrade pip wheel setuptools
pip install -r requirements.txt
deactivate
Pop-Location
Write-Host "[OK] Python backend" -ForegroundColor Green
Write-Host ""

# Frontend — React app dependencies
Write-Host "[2/4] Installing frontend dependencies..." -ForegroundColor Yellow
Push-Location frontend
npm install
Pop-Location
Write-Host "[OK] Frontend" -ForegroundColor Green
Write-Host ""

# Desktop — Electron shell dependencies
Write-Host "[3/4] Installing desktop (Electron) dependencies..." -ForegroundColor Yellow
Push-Location desktop
npm install
Pop-Location
Write-Host "[OK] Desktop" -ForegroundColor Green
Write-Host ""

# Environment file
Write-Host "[4/4] Setting up environment..." -ForegroundColor Yellow
if (-not (Test-Path .env)) {
    Copy-Item .env.example .env
    Write-Host "[OK] Created .env from .env.example - edit it with your API keys." -ForegroundColor Green
} else {
    Write-Host "[SKIP] .env already exists." -ForegroundColor Gray
}

# Create data directory for backend
New-Item -ItemType Directory -Force -Path backend\data | Out-Null

Write-Host ""
Write-Host "=== Bootstrap complete ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:"
Write-Host "  1. Edit .env with your API keys (LiveKit, Anthropic, Deepgram, Cartesia)"
Write-Host "  2. Start development servers:"
Write-Host "     Terminal 1: cd backend && .\.venv\Scripts\Activate.ps1 && python main.py"
Write-Host "     Terminal 2: cd frontend && npm run dev"
Write-Host "     Terminal 3: cd desktop && set RENDERER_URL=http://localhost:5173 && npm run dev"
Write-Host ""
