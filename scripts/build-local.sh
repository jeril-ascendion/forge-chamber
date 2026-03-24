#!/bin/bash
# Forge Chamber — Local Build Script
# Tests the full build pipeline before tagging a release.
# Usage: chmod +x scripts/build-local.sh && ./scripts/build-local.sh

set -e

echo "=== Forge Chamber Local Build ==="
echo ""

# Step 1: Build Python sidecar
echo "Step 1/4: Building Python sidecar..."
cd backend
source .venv/bin/activate
pyinstaller forge_chamber.spec --clean
SIDECAR_SIZE=$(du -sh dist/forge_chamber.exe 2>/dev/null | cut -f1 || echo "N/A")
echo "Sidecar: $SIDECAR_SIZE"
deactivate
cd ..
echo ""

# Step 2: Build React frontend
echo "Step 2/4: Building React frontend..."
cd frontend
npm run build
FRONTEND_SIZE=$(du -sh dist/ 2>/dev/null | cut -f1 || echo "N/A")
echo "Frontend: $FRONTEND_SIZE"
cd ..
echo ""

# Step 3: Package Electron installer
echo "Step 3/4: Packaging Electron installer..."
cd desktop
npm run build
cd ..
echo ""

# Step 4: Summary
echo "Step 4/4: Build complete."
echo ""
echo "Artifacts:"
echo "  Sidecar:   backend/dist/forge_chamber.exe ($SIDECAR_SIZE)"
echo "  Frontend:  frontend/dist/ ($FRONTEND_SIZE)"
ls -lh desktop/dist/*.exe 2>/dev/null && echo "" || echo "  Installer: desktop/dist/ (check output)"
echo ""
echo "Test the installer on a clean Windows machine before tagging."
