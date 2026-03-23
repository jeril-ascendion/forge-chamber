# Forge Chamber — Developer Guide

> Complete setup guide for building Forge Chamber on Windows and macOS.
> Covers every tool, configuration, and command needed to go from zero to a running build.

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Windows Setup](#2-windows-setup)
3. [macOS Setup](#3-macos-setup)
4. [Project Setup (Both Platforms)](#4-project-setup-both-platforms)
5. [API Keys and Credentials](#5-api-keys-and-credentials)
6. [Running in Development](#6-running-in-development)
7. [Building for Distribution](#7-building-for-distribution)
8. [Project Structure Deep Dive](#8-project-structure-deep-dive)
9. [Troubleshooting](#9-troubleshooting)

---

## 1. Architecture Overview

Forge Chamber is a three-layer application:

```
┌─────────────────────────────────────────────┐
│  Electron Shell (Node.js + Chromium)        │
│  Manages app lifecycle, spawns sidecar,     │
│  handles OS integration                     │
├─────────────────────────────────────────────┤
│  React Renderer (Vite + TypeScript)         │
│  All UI — voice panel, transcript,          │
│  agent cards, skill radar                   │
├─────────────────────────────────────────────┤
│  Python Sidecar (FastAPI + LiveKit Agents)  │
│  LLM calls, voice pipeline, RAG,            │
│  SQLite, ChromaDB                           │
└─────────────────────────────────────────────┘
         │                    │
    LiveKit Cloud         Anthropic API
   (WebRTC relay)        (Claude Sonnet/Haiku)
         │                    │
   Deepgram STT          Cartesia TTS
```

**Key design decision:** The sidecar is compiled to a standalone `.exe` via PyInstaller. No Python installation required on end-user machines.

---

## 2. Windows Setup

### 2.1 System Requirements

- Windows 10 or 11 (64-bit)
- 16 GB RAM minimum
- 10 GB free disk space (for tools + project + Python packages)
- Internet connection for API calls

### 2.2 Install Node.js

Download from [nodejs.org](https://nodejs.org) — install **v20 LTS**.

Verify:
```powershell
node --version   # v20.x.x
npm --version    # 10.x.x
```

### 2.3 Install Python 3.11

Download from [python.org/downloads](https://www.python.org/downloads/release/python-3119/).

**Critical install options:**
- Check "Add Python to PATH"
- Check "Install pip"
- Check "Install for all users" (recommended)

Verify:
```powershell
python --version   # Python 3.11.x
pip --version      # pip 24.x
```

> **Important:** Python 3.12+ has compatibility issues with some LiveKit plugins in early 2025. Use 3.11.x exactly.

### 2.4 Install Git

Download from [git-scm.com](https://git-scm.com/download/win).

During install, select:
- "Git from the command line and also from 3rd-party software"
- "Use bundled OpenSSH"
- Line ending: "Checkout Windows-style, commit Unix-style"

```powershell
git --version   # git version 2.x.x
```

### 2.5 Install Visual Studio Build Tools

Required for compiling Python C extensions (numpy, sentence-transformers).

Download [Visual Studio Build Tools 2022](https://visualstudio.microsoft.com/visual-cpp-build-tools/).

Select workload: **Desktop development with C++**

Minimum components:
- MSVC v143 build tools
- Windows 10 SDK
- CMake tools

This download is ~2–3 GB and takes 10–15 minutes.

### 2.6 Install Windows Terminal (Recommended)

From Microsoft Store: search "Windows Terminal". Much better than PowerShell default.

### 2.7 Configure PowerShell Execution Policy

```powershell
# Run PowerShell as Administrator
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 2.8 Optional: Install WSL2

If you prefer a Linux-like environment for Python work:

```powershell
# In PowerShell as Administrator
wsl --install
# Reboot required
# Then install Ubuntu from Microsoft Store
```

WSL2 is optional — everything can be done in native Windows.

---

## 3. macOS Setup

### 3.1 System Requirements

- macOS 12 (Monterey) or later
- 16 GB RAM minimum
- 10 GB free disk space
- Intel or Apple Silicon (M1/M2/M3/M4)

### 3.2 Install Homebrew

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

For Apple Silicon, add to your `~/.zshrc`:
```bash
eval "$(/opt/homebrew/bin/brew shellenv)"
```

### 3.3 Install Node.js via nvm

```bash
# Install nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash

# Reload shell
source ~/.zshrc

# Install Node 20 LTS
nvm install 20
nvm use 20
nvm alias default 20

node --version   # v20.x.x
```

### 3.4 Install Python 3.11 via pyenv

```bash
# Install pyenv
brew install pyenv

# Add to ~/.zshrc
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.zshrc
echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.zshrc
echo 'eval "$(pyenv init -)"' >> ~/.zshrc
source ~/.zshrc

# Install Python 3.11
pyenv install 3.11.9
pyenv global 3.11.9

python --version   # Python 3.11.9
```

### 3.5 Install Xcode Command Line Tools

```bash
xcode-select --install
```

### 3.6 Install Git

```bash
brew install git
git --version   # git version 2.x.x
```

---

## 4. Project Setup (Both Platforms)

### 4.1 Clone the Repository

```bash
git clone https://github.com/ascendion/forge-chamber.git
cd forge-chamber
```

### 4.2 Set Up Python Virtual Environment

**Windows (PowerShell):**
```powershell
cd sidecar
python -m venv .venv
.venv\Scripts\Activate.ps1

# You should see (.venv) in your prompt
pip install --upgrade pip
pip install -r requirements.txt
```

**macOS/Linux (bash/zsh):**
```bash
cd sidecar
python -m venv .venv
source .venv/bin/activate

# You should see (.venv) in your prompt
pip install --upgrade pip
pip install -r requirements.txt
```

> **Note:** `pip install -r requirements.txt` takes 5–10 minutes the first time.
> sentence-transformers downloads the `all-MiniLM-L6-v2` model (~80MB) on first run.

#### sidecar/requirements.txt

```txt
# Web framework
fastapi==0.111.0
uvicorn[standard]==0.30.1
python-multipart==0.0.9

# LiveKit voice pipeline
livekit-agents==0.8.7
livekit-plugins-anthropic==0.3.2
livekit-plugins-deepgram==0.6.5
livekit-plugins-silero==0.6.3
livekit-plugins-cartesia==0.3.2
livekit==0.17.3

# LLM orchestration
langchain==0.2.12
langgraph==0.1.19
anthropic==0.34.2

# RAG pipeline
llama-index==0.10.67
llama-index-readers-web==0.2.2
llama-index-readers-file==0.2.2
llama-index-embeddings-huggingface==0.3.1

# Vector store
chromadb==0.5.11

# Embeddings (local, no API needed)
sentence-transformers==3.0.1

# Database
sqlalchemy==2.0.32
aiosqlite==0.20.0

# Configuration
pydantic-settings==2.4.0
python-dotenv==1.0.1

# Build
pyinstaller==6.9.0

# Testing
pytest==8.3.2
pytest-asyncio==0.23.8
httpx==0.27.0
```

### 4.3 Set Up Electron + Renderer

```bash
# Install Electron dependencies
cd ../electron
npm install

# Install Renderer dependencies
cd ../renderer
npm install
```

#### electron/package.json key dependencies

```json
{
  "dependencies": {
    "electron-keytar": "^7.9.0",
    "electron-updater": "^6.1.7"
  },
  "devDependencies": {
    "electron": "^28.3.0",
    "electron-builder": "^24.13.3"
  }
}
```

#### renderer/package.json key dependencies

```json
{
  "dependencies": {
    "@livekit/components-react": "^2.3.0",
    "@livekit/components-styles": "^1.1.0",
    "livekit-client": "^2.4.0",
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "zustand": "^4.5.4"
  },
  "devDependencies": {
    "@types/react": "^18.3.3",
    "@vitejs/plugin-react": "^4.3.1",
    "autoprefixer": "^10.4.20",
    "postcss": "^8.4.41",
    "tailwindcss": "^3.4.10",
    "typescript": "^5.5.4",
    "vite": "^5.4.2"
  }
}
```

### 4.4 Configure Environment Variables

```bash
# Copy template
cp .env.example .env

# Edit .env with your API keys (see Section 5)
```

### 4.5 Initialize the Database

```bash
cd sidecar
source .venv/bin/activate   # or .venv\Scripts\Activate.ps1 on Windows
python -c "from db.database import init_db; init_db('./data')"
```

---

## 5. API Keys and Credentials

### 5.1 LiveKit Cloud (Free Tier — No Credit Card)

1. Go to [livekit.io/cloud](https://livekit.io/cloud)
2. Sign up with GitHub
3. Create a new project: "forge-chamber-dev"
4. Go to Settings → Keys
5. Copy URL, API Key, API Secret

Free tier includes: 1,000 agent session minutes/month + 5,000 participant minutes. More than enough for development.

### 5.2 Anthropic API

1. Go to [console.anthropic.com](https://console.anthropic.com)
2. Create an API key
3. If using Claude Max subscription, the key is under your account settings

Models used:
- `claude-haiku-4-5` — orchestrator routing (cheap, fast)
- `claude-sonnet-4-5` — agent utterance generation (quality)

### 5.3 Deepgram (Free $200 Credit)

1. Go to [deepgram.com](https://deepgram.com)
2. Sign up → Dashboard → Create API Key
3. $200 credit = ~46,000 minutes of audio at Nova-2 pricing

### 5.4 Cartesia (Free Tier)

1. Go to [cartesia.ai](https://cartesia.ai)
2. Sign up → Dashboard → API Keys
3. Free tier is sufficient for development

#### Voice IDs for Each Agent

```python
VOICE_IDS = {
    "sre":       "694f9389-aac1-45b6-b726-9d9369183238",  # Deep, measured male
    "sys_arch":  "a0e99841-438c-4a64-b679-ae501e7d6091",  # Warm, thoughtful female
    "cloud_eng": "63ff761f-c1e8-414b-b969-d1833d1c870c",  # Neutral, efficient male
    "java_dev":  "b7d50908-b17c-442d-ad8d-810c63997ed9",  # Crisp, methodical male
    "ui_dev":    "156fb8d2-335b-4950-9cb3-a2d33befec77",  # Energetic, informal
}
```

> **Tip:** Test voices at [play.cartesia.ai](https://play.cartesia.ai) before committing to IDs.

---

## 6. Running in Development

You need 4 terminal windows.

### Terminal 1: Python Sidecar

```bash
cd sidecar
source .venv/bin/activate    # macOS/Linux
# .venv\Scripts\Activate.ps1  # Windows

export FORGE_DATA_DIR=./data
export FORGE_PORT=8765

python main.py
```

Expected output:
```
INFO:     Started server process
INFO:     Waiting for application startup
INFO:     Application startup complete
INFO:     Uvicorn running on http://127.0.0.1:8765
```

### Terminal 2: LiveKit Agent Worker

```bash
cd sidecar
source .venv/bin/activate

python voice/livekit_worker.py dev
```

Expected output:
```
INFO livekit - connected to livekit server
INFO agent - starting worker...
INFO agent - waiting for jobs...
```

### Terminal 3: React Dev Server

```bash
cd renderer
npm run dev
```

Expected output:
```
  VITE v5.x ready in 300ms
  → Local:   http://localhost:5173/
```

### Terminal 4: Electron (Dev Mode)

```bash
cd electron
RENDERER_URL=http://localhost:5173 npm run dev
```

The app window opens. Changes to React code hot-reload instantly.
Changes to the Python sidecar require restarting Terminal 1.

### Health Check

Verify all layers are running:
```bash
curl http://localhost:8765/health
# → {"status":"ok","version":"1.0.0"}
```

---

## 7. Building for Distribution

### 7.1 Build Python Sidecar (Windows)

```powershell
cd sidecar
.venv\Scripts\Activate.ps1
pyinstaller forge_chamber.spec
```

Expected output: `sidecar/dist/forge_chamber.exe` (~180–200MB)

**If build fails with missing module errors:**
```powershell
# Add missing imports to hiddenimports in .spec file
# Then rebuild
```

### 7.2 Build Python Sidecar (macOS)

```bash
cd sidecar
source .venv/bin/activate
pyinstaller forge_chamber.spec
```

Output: `sidecar/dist/forge_chamber` (~170MB binary)

### 7.3 Build React Renderer

```bash
cd renderer
npm run build
```

Output: `renderer/dist/` — static files ready for Electron to load.

### 7.4 Build Electron Installer (Windows)

```powershell
cd electron
npm run build
```

Output: `electron/dist/Forge Chamber Setup 1.0.0.exe` (~220MB)

This is the file you distribute to engineers.

### 7.5 Build on macOS (for macOS target)

```bash
cd electron
npm run build:mac
```

Output: `electron/dist/Forge Chamber-1.0.0.dmg`

> **Cross-platform builds:** You cannot build a Windows `.exe` from macOS or vice versa without additional tooling. Build on the target OS.

### 7.6 Publish a Release (GitHub)

```bash
# Tag the release
git tag v1.0.0
git push origin v1.0.0

# Build and upload to GitHub Releases automatically
cd electron
GH_TOKEN=your_github_token npm run publish
```

Engineers download from your GitHub Releases page. `electron-updater` checks this URL on every app launch.

---

## 8. Project Structure Deep Dive

### 8.1 `electron/main.js` — What it does

1. On app ready: creates browser window, starts sidecar
2. Sidecar starts as a child process — output hidden from user
3. Polls `http://localhost:8765/health` until sidecar responds
4. Shows `splash.html` during sidecar startup (prevents blank window)
5. Once sidecar ready: loads the React renderer
6. Registers IPC handlers for file system, keychain, updates
7. On app quit: kills sidecar process cleanly

### 8.2 `sidecar/main.py` — What it does

1. Reads config from env vars (`FORGE_DATA_DIR`, `FORGE_PORT`)
2. Initializes SQLite database (creates tables if not exist)
3. Starts ChromaDB embedded client
4. Loads sentence-transformers embedding model (one-time, ~3s)
5. Starts FastAPI server on `127.0.0.1:{FORGE_PORT}`
6. Runs until Electron kills the process

### 8.3 `sidecar/voice/livekit_worker.py` — What it does

1. Connects to LiveKit Cloud as an agent worker
2. Waits for a job (triggered by `POST /session/start`)
3. On job received: creates debate session, spawns agent VoiceAssistants
4. Manages the autonomous debate loop (LangGraph)
5. Handles human speech events — pauses debate, resumes after
6. Publishes transcript updates via LiveKit data channel
7. On session end: triggers debrief generation

### 8.4 `renderer/src/pages/RoomActive.tsx` — What it does

1. Connects to LiveKit room using token from `/session/start`
2. Subscribes to data channel messages (transcript, speaker changes)
3. Renders real-time transcript as turns arrive
4. Shows active speaker indicator per AgentPanel card
5. Handles "Join Debate" — enables local mic, publishes human_speaking event
6. Handles session end → navigates to Debrief page

---

## 9. Troubleshooting

### Sidecar won't start

```powershell
# Check if port is in use
netstat -ano | findstr :8765

# Kill the process using it
taskkill /PID <pid> /F

# Check Python version
python --version  # Must be 3.11.x

# Try running manually to see error
cd sidecar
python main.py
```

### "sentence-transformers model not found"

```bash
# The model downloads on first run — needs internet
# If behind a corporate proxy:
pip install sentence-transformers --proxy http://your-proxy:port
```

### LiveKit agent won't connect

```bash
# Verify credentials
python -c "
from livekit import api
import os
client = api.LiveKitAPI(os.getenv('LIVEKIT_URL'), os.getenv('LIVEKIT_API_KEY'), os.getenv('LIVEKIT_API_SECRET'))
print('Connected')
"
```

### Electron shows blank window

```bash
# Check sidecar is running
curl http://localhost:8765/health

# Check renderer is running
curl http://localhost:5173

# Check RENDERER_URL env var is set correctly
```

### PyInstaller build fails

```bash
# Common fix: explicitly add all imports
pip install pyinstaller
pyinstaller --collect-all livekit_agents --collect-all chromadb forge_chamber.spec
```

### Windows SmartScreen blocks installer

This happens when the installer is not code-signed. For internal distribution:
1. Tell engineers: "More info → Run anyway"
2. Or: get IT to sign the exe with the org certificate
3. Or: distribute as a ZIP instead of NSIS installer

### Audio not working in Electron

```javascript
// electron/main.js — add this before app.whenReady()
app.commandLine.appendSwitch('autoplay-policy', 'no-user-gesture-required')
app.commandLine.appendSwitch('use-fake-ui-for-media-stream', 'false')
```

### High memory usage

The sentence-transformers model uses ~400MB RAM. This is expected.
If total sidecar RAM exceeds 600MB, check for ChromaDB collection size.
Limit context chunks per Room to 200 max.

---

## Quick Reference

### Ports
| Service | Port |
|---------|------|
| FastAPI sidecar | 8765 |
| React dev server | 5173 |
| LiveKit (local dev) | n/a — uses LiveKit Cloud |

### Key Commands
```bash
# Start all dev services
./scripts/dev.sh

# Build everything
./scripts/build-all.sh

# Run Python tests
cd sidecar && pytest tests/ -v

# Run type check
cd renderer && npx tsc --noEmit
```

### Data Locations
| Platform | Data Directory |
|----------|----------------|
| Windows | `%APPDATA%\ForgeChamber\` |
| macOS | `~/Library/Application Support/ForgeChamber/` |
| Linux | `~/.config/ForgeChamber/` |

Contents: `forge_chamber.db` (SQLite), `chroma/` (vector store), `sources.json`, `tmp/` (file uploads)
