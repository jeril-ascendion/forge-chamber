# build-windows.ps1 — Build Forge Chamber portable exe for Windows
# Run from repo root: powershell -ExecutionPolicy Bypass -File scripts/build-windows.ps1
#
# Prerequisites:
#   - Node.js 20+
#   - Python 3.11.9
#   - PyInstaller 6.9.0 (pip install pyinstaller==6.9.0)
#
# Output: desktop/dist/Forge-Chamber-1.0.0.exe (portable, no installer needed)

$ErrorActionPreference = "Stop"

Write-Host "=== Forge Chamber Windows Build ===" -ForegroundColor Cyan

# Disable code signing — we distribute unsigned portable exe
$env:CSC_IDENTITY_AUTO_DISCOVERY = "false"
Remove-Item Env:WIN_CSC_LINK -ErrorAction SilentlyContinue

# Step 1: Build Python sidecar
Write-Host "`n[1/4] Building Python sidecar..." -ForegroundColor Yellow
Push-Location backend
if (-not (Test-Path ".venv/Scripts/activate.ps1")) {
    Write-Host "  Creating Python virtual environment..."
    python -m venv .venv
    & .venv/Scripts/activate.ps1
    pip install -r requirements.txt
    pip install pyinstaller==6.9.0
} else {
    & .venv/Scripts/activate.ps1
}
pyinstaller forge_chamber.spec --clean --noconfirm
$sidecarSize = (Get-ChildItem -Path dist/forge_chamber -Recurse | Measure-Object -Property Length -Sum).Sum / 1MB
Write-Host "  Sidecar built: $([math]::Round($sidecarSize, 1)) MB" -ForegroundColor Green
Pop-Location

# Step 2: Build React frontend
Write-Host "`n[2/4] Building React frontend..." -ForegroundColor Yellow
Push-Location frontend
npm ci
npm run build
Pop-Location

# Step 3: Install Electron dependencies
Write-Host "`n[3/4] Installing Electron dependencies..." -ForegroundColor Yellow
Push-Location desktop
npm install
Pop-Location

# Step 4: Build portable exe (no code signing, no NSIS installer)
Write-Host "`n[4/4] Building Electron portable exe..." -ForegroundColor Yellow
Push-Location desktop
npx electron-builder --win portable --x64 --publish never
Pop-Location

# Report output
$outputExe = Get-ChildItem -Path desktop/dist -Filter "*.exe" | Select-Object -First 1
if ($outputExe) {
    $exeSize = [math]::Round($outputExe.Length / 1MB, 1)
    Write-Host "`n=== Build Complete ===" -ForegroundColor Green
    Write-Host "Output: desktop/dist/$($outputExe.Name) ($exeSize MB)"
} else {
    Write-Host "`n=== Build Failed ===" -ForegroundColor Red
    Write-Host "No .exe found in desktop/dist/"
    exit 1
}
