#!/bin/bash
set -e

echo "=== Forge Chamber Bootstrap ==="
echo ""

# Check prerequisites
command -v python3 >/dev/null 2>&1 || { echo "ERROR: python3 not found. Install Python 3.11.9."; exit 1; }
command -v node >/dev/null 2>&1 || { echo "ERROR: node not found. Install Node.js 20 LTS."; exit 1; }
command -v npm >/dev/null 2>&1 || { echo "ERROR: npm not found. Install Node.js 20 LTS."; exit 1; }

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
NODE_VERSION=$(node --version)
echo "Python: $PYTHON_VERSION"
echo "Node:   $NODE_VERSION"
echo ""

# Backend — Python virtual environment + dependencies
echo "[1/4] Setting up Python backend..."
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip wheel setuptools
pip install -r requirements.txt
deactivate
cd ..
echo "[OK] Python backend"
echo ""

# Frontend — React app dependencies
echo "[2/4] Installing frontend dependencies..."
cd frontend
npm install
cd ..
echo "[OK] Frontend"
echo ""

# Desktop — Electron shell dependencies
echo "[3/4] Installing desktop (Electron) dependencies..."
cd desktop
npm install
cd ..
echo "[OK] Desktop"
echo ""

# Environment file
echo "[4/4] Setting up environment..."
if [ ! -f .env ]; then
  cp .env.example .env
  echo "[OK] Created .env from .env.example — edit it with your API keys."
else
  echo "[SKIP] .env already exists."
fi

# Create data directory for backend
mkdir -p backend/data

echo ""
echo "=== Bootstrap complete ==="
echo ""
echo "Next steps:"
echo "  1. Edit .env with your API keys (LiveKit, Anthropic, Deepgram, Cartesia)"
echo "  2. Start development servers:"
echo "     Terminal 1: cd backend && source .venv/bin/activate && python main.py"
echo "     Terminal 2: cd frontend && npm run dev"
echo "     Terminal 3: cd desktop && RENDERER_URL=http://localhost:5173 npm run dev"
echo ""
