# Forge Chamber — Detailed Development Guide

**Version:** 1.0 | **Author:** Jeril John Panicker, Solutions Architect, Ascendion  
**Program:** Forge Engineering Excellence | **Status:** Active Development

---

## Table of Contents

- [Section 1: Environment Setup — Windows](#section-1-environment-setup--windows)
- [Section 2: Environment Setup — macOS](#section-2-environment-setup--macos)
- [Section 3: Project Bootstrap (Both Platforms)](#section-3-project-bootstrap-both-platforms)
- [Section 4: EPICs & Tasks](#section-4-epics--tasks)
- [Section 5: CI/CD Pipeline](#section-5-cicd-pipeline)
- [Section 6: Process & Workflow](#section-6-process--workflow)
- [Section 7: Observability & Operations](#section-7-observability--operations)
- [Section 8: Reference](#section-8-reference)

---

## Section 1: Environment Setup — Windows

### System Requirements
- Windows 10 (build 19041+) or Windows 11, 64-bit
- 16 GB RAM minimum
- 15 GB free disk space
- Internet connection

### Step 1 — Windows Terminal & PowerShell 7

```powershell
# Install from Microsoft Store, then:
winget install Microsoft.PowerShell

# Run PowerShell 7 as Administrator:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Step 2 — Git

Download from git-scm.com/download/win. During install:
- "Git from the command line and also from 3rd-party software"
- "Use bundled OpenSSH"
- Line endings: "Checkout Windows-style, commit Unix-style"

```powershell
git --version   # git version 2.44.x or later
git config --global user.name "Your Name"
git config --global user.email "you@ascendion.com"
git config --global init.defaultBranch main
```

### Step 3 — Node.js 20 LTS

Download the LTS installer from nodejs.org. Check "Automatically install the necessary tools" — this opens a second terminal to install Chocolatey and build tools. Let it complete fully.

```powershell
node --version   # v20.x.x
npm --version    # 10.x.x
```

### Step 4 — Python 3.11.9 (EXACT VERSION)

Download from python.org/downloads/release/python-3119/ → "Windows installer (64-bit)"

> **CRITICAL:** Use Python 3.11.9 exactly. Python 3.12+ breaks several LiveKit plugins. Do NOT use Microsoft Store Python — it has sandboxing issues with PyInstaller.

During install:
- Check "Add Python to PATH"
- Check "Install launcher for all users"
- Choose "Customize installation" → check all optional features
- Advanced Options: check "Add Python to environment variables"

```powershell
python --version   # Python 3.11.9
pip --version      # pip 24.x from ...Python311...
```

### Step 5 — Visual Studio Build Tools 2022

Required for compiling C extensions (numpy, sentence-transformers, chromadb).

Download "Build Tools for Visual Studio 2022" from visualstudio.microsoft.com/visual-cpp-build-tools/

Select workload: **Desktop development with C++**

Minimum components:
- MSVC v143 — VS 2022 C++ x64/x86 build tools (Latest)
- Windows 11 SDK (10.0.22621.0) or Windows 10 SDK
- C++ CMake tools for Windows

> This is 3–4 GB and takes 15–25 minutes. Do not skip — pip install will fail for binary packages without it.

### Step 6 — Rust (Required for ChromaDB)

```powershell
winget install Rustlang.Rustup
# Reload terminal
rustc --version   # rustc 1.79.x or later
```

### Step 7 — Firewall Rules

```powershell
# Run as Administrator
New-NetFirewallRule -DisplayName "Forge Chamber LiveKit UDP" `
  -Direction Inbound -Protocol UDP `
  -LocalPort 50000-50020 -Action Allow

New-NetFirewallRule -DisplayName "Forge Chamber Dev Ports" `
  -Direction Inbound -Protocol TCP `
  -LocalPort 5173,8765 -Action Allow
```

### Step 8 — VS Code

```powershell
winget install Microsoft.VisualStudioCode
```

**Required extensions** (Ctrl+Shift+X):

| Extension | Publisher | Purpose |
|-----------|-----------|---------|
| Python | Microsoft | Python IntelliSense, linting |
| Pylance | Microsoft | Type checking |
| ESLint | Microsoft | JS/TS linting |
| Prettier | Prettier | Code formatting |
| Tailwind CSS IntelliSense | Bradlc | TailwindCSS autocomplete |
| Thunder Client | Rangav | API testing |
| GitLens | GitKraken | Git history |
| Error Lens | Alexander | Inline errors |

---

## Section 2: Environment Setup — macOS

### System Requirements
- macOS 12 (Monterey) or later — tested on Sonoma (Intel + Apple Silicon)
- 16 GB RAM minimum
- 15 GB free disk space

### Step 1 — Xcode Command Line Tools

```bash
xcode-select --install
# Click "Install" in dialog — 5-10 minutes
clang --version   # Apple clang version 15.x
```

### Step 2 — Homebrew

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Apple Silicon only — add to ~/.zshrc:
eval "$(/opt/homebrew/bin/brew shellenv)"
source ~/.zshrc
brew --version   # Homebrew 4.x
```

### Step 3 — Git

```bash
brew install git
git --version   # git version 2.44.x
git config --global user.name "Your Name"
git config --global user.email "you@ascendion.com"
git config --global init.defaultBranch main
```

### Step 4 — Node.js 20 LTS via nvm

```bash
# Install nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash

# Add to ~/.zshrc (installer does this, but verify):
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
source ~/.zshrc

# Install Node 20 LTS
nvm install 20
nvm use 20
nvm alias default 20
node --version   # v20.x.x
```

### Step 5 — Python 3.11.9 via pyenv

```bash
# Install pyenv
brew install pyenv

# Add to ~/.zshrc:
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.zshrc
echo '[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.zshrc
echo 'eval "$(pyenv init -)"' >> ~/.zshrc
source ~/.zshrc

# Install Python 3.11.9
pyenv install 3.11.9
pyenv global 3.11.9
python --version   # Python 3.11.9
```

### Step 6 — Rust

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source "$HOME/.cargo/env"
rustc --version   # rustc 1.79.x
```

### Step 7 — Additional Tools

```bash
brew install wget curl jq
brew install --cask visual-studio-code

# Developer mode for Electron
spctl developer-mode enable-terminal

# Apple Silicon: Rosetta for some binary deps
softwareupdate --install-rosetta --agree-to-license
```

---

## Section 3: Project Bootstrap (Both Platforms)

### Clone & Bootstrap

```bash
git clone https://github.com/ascendion/forge-chamber.git
cd forge-chamber

# macOS/Linux:
chmod +x scripts/bootstrap.sh && ./scripts/bootstrap.sh

# Windows:
.\scripts\bootstrap.ps1
```

### bootstrap.sh

```bash
#!/bin/bash
set -e
echo "=== Forge Chamber Bootstrap ==="

cd sidecar
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip wheel setuptools
pip install -r requirements.txt
echo "[OK] Python sidecar"

cd ../electron && npm install
echo "[OK] Electron"

cd ../renderer && npm install
echo "[OK] Renderer"

mkdir -p ../sidecar/data
cp ../.env.example ../.env
echo "[OK] Bootstrap complete. Edit .env with your API keys."
```

### .env File

```env
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=your_livekit_api_key
LIVEKIT_API_SECRET=your_livekit_api_secret
ANTHROPIC_API_KEY=sk-ant-your-key
DEEPGRAM_API_KEY=your_deepgram_key
CARTESIA_API_KEY=your_cartesia_key

# Set automatically at runtime — do not edit:
FORGE_DATA_DIR=
FORGE_PORT=8765
```

### Running in Development (4 terminals)

```bash
# Terminal 1 — Python sidecar
cd sidecar && source .venv/bin/activate && python main.py

# Terminal 2 — LiveKit agent worker
cd sidecar && source .venv/bin/activate && python voice/livekit_worker.py dev

# Terminal 3 — React renderer
cd renderer && npm run dev

# Terminal 4 — Electron
cd electron && RENDERER_URL=http://localhost:5173 npm run dev

# Health check
curl http://localhost:8765/health
# → {"status":"ok","version":"1.0.0"}
```

### .vscode/settings.json

```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/sidecar/.venv/bin/python",
  "editor.formatOnSave": true,
  "[python]": { "editor.defaultFormatter": "ms-python.black-formatter" },
  "[typescript]": { "editor.defaultFormatter": "esbenp.prettier-vscode" },
  "[typescriptreact]": { "editor.defaultFormatter": "esbenp.prettier-vscode" },
  "tailwindCSS.experimental.classRegex": [
    ["clsx\\(([^)]*)\\)", "\"([^\"]*)\""]
  ],
  "typescript.preferences.importModuleSpecifier": "relative"
}
```

---

## Section 4: EPICs & Tasks

### Complexity Scale

| Score | Points | Duration | Description |
|-------|--------|----------|-------------|
| S — Small | 1–2 | 0.5–1 day | Isolated change, clear solution |
| M — Medium | 3–5 | 1–2 days | Some design decisions |
| L — Large | 6–9 | 2–4 days | Multiple components |
| XL — Extra Large | 10+ | 4–8 days | Complex system design |

### Timeline at a Glance

| EPIC | Title | Weeks | Days | Complexity |
|------|-------|-------|------|------------|
| E1 | Foundation & Repository Setup | Week 1 | 5d | Low |
| E2 | Electron Shell & App Infrastructure | Weeks 1–2 | 7d | Medium |
| E3 | Python Sidecar & FastAPI Backend | Weeks 2–3 | 8d | Medium |
| E4 | Voice Pipeline Integration | Weeks 3–4 | 8d | High |
| E5 | Multi-Agent Debate Engine | Weeks 4–6 | 12d | Very High |
| E6 | RAG Pipeline & Context Ingestion | Weeks 6–7 | 7d | High |
| E7 | React UI Implementation | Weeks 5–8 | 14d | High |
| E8 | Skills, XP & Progress Tracking | Weeks 8–9 | 6d | Medium |
| E9 | Testing & Quality Assurance | Weeks 9–10 | 8d | Medium |
| E10 | CI/CD Pipeline & Distribution | Weeks 10–12 | 10d | High |

---

## EPIC 1 — Foundation & Repository Setup
**Timeline:** Week 1 | **Complexity:** Low | **Total:** 5 days

### E1-T1 — Repository & Directory Structure
**Complexity:** S | **Duration:** 1 day

**Description:** Initialize repo with exact directory structure from CLAUDE.md, .gitignore, .env.example.

**Acceptance Criteria:**
- [ ] Repository initialized and pushed to GitHub (ascendion/forge-chamber)
- [ ] All directories from CLAUDE.md exist: electron/, renderer/, sidecar/, scripts/
- [ ] .gitignore excludes: node_modules, .venv, __pycache__, .env, dist, *.exe, *.pyc, sidecar/data
- [ ] .env.example has all 6 API key variable names with inline comments
- [ ] README.md present with one-line description and link to full docs

**Subtasks:**
- `E1-T1-S1` Create all directories — `mkdir -p` for all CLAUDE.md paths — 30m
- `E1-T1-S2` Write .gitignore — Python, Node, Electron, VS Code, OS patterns — 20m
- `E1-T1-S3` Write .env.example — all 6 variables with comments — 20m
- `E1-T1-S4` Initial commit and push to GitHub — 10m

---

### E1-T2 — Python Sidecar Package Setup
**Complexity:** M | **Duration:** 2 days

**Description:** Create requirements.txt with all dependencies pinned to exact versions. Verify clean install on both platforms.

**Acceptance Criteria:**
- [ ] requirements.txt with all packages pinned (no version ranges)
- [ ] Virtual environment created at sidecar/.venv on both platforms
- [ ] `pip install -r requirements.txt` completes with 0 errors on Windows 11 and macOS
- [ ] sentence-transformers model all-MiniLM-L6-v2 downloads and loads without error
- [ ] ChromaDB client initializes at test directory without error
- [ ] Import test passes: fastapi, livekit, chromadb, llama_index, anthropic all importable

**Subtasks:**
- `E1-T2-S1` Write requirements.txt — all packages from CLAUDE.md tech stack — 45m
- `E1-T2-S2` Write bootstrap.sh and bootstrap.ps1 — 60m
- `E1-T2-S3` Test install on Windows — fresh environment — 90m
- `E1-T2-S4` Test install on macOS (Intel + Apple Silicon if available) — 60m

**requirements.txt (exact):**
```
fastapi==0.111.0
uvicorn[standard]==0.30.1
python-multipart==0.0.9
livekit-agents==0.8.7
livekit-plugins-anthropic==0.3.2
livekit-plugins-deepgram==0.6.5
livekit-plugins-silero==0.6.3
livekit-plugins-cartesia==0.3.2
livekit==0.17.3
langchain==0.2.12
langgraph==0.1.19
anthropic==0.34.2
llama-index==0.10.67
llama-index-readers-web==0.2.2
llama-index-readers-file==0.2.2
llama-index-embeddings-huggingface==0.3.1
chromadb==0.5.11
sentence-transformers==3.0.1
sqlalchemy==2.0.32
aiosqlite==0.20.0
pydantic-settings==2.4.0
python-dotenv==1.0.1
pyinstaller==6.9.0
pytest==8.3.2
pytest-asyncio==0.23.8
pytest-cov==5.0.0
httpx==0.27.0
```

---

### E1-T3 — Node.js Package Setup
**Complexity:** S | **Duration:** 1 day

**Acceptance Criteria:**
- [ ] electron/package.json with all deps, correct main entry point, build config
- [ ] renderer/package.json with React, Vite, TypeScript, Tailwind, LiveKit
- [ ] npm install runs cleanly in both directories
- [ ] TypeScript strict mode enabled in renderer/tsconfig.json
- [ ] Vite dev server starts on port 5173

**Subtasks:**
- `E1-T3-S1` electron/package.json — electron 28, electron-builder, keytar, updater — 30m
- `E1-T3-S2` renderer/package.json — react 18, vite 5, tailwind 3, livekit, zustand — 30m
- `E1-T3-S3` tsconfig.json — strict, path aliases, jsx: react-jsx — 20m
- `E1-T3-S4` vite.config.ts — react plugin, proxy to :8765 — 20m
- `E1-T3-S5` tailwind.config.ts — content paths, CSS variables — 20m

---

## EPIC 2 — Electron Shell & App Infrastructure
**Timeline:** Weeks 1–2 | **Complexity:** Medium | **Total:** 7 days

### E2-T1 — Electron Main Process
**Complexity:** L | **Duration:** 3 days

**Description:** Implement main.js with window management, sidecar spawning, health polling, and lifecycle management.

**Acceptance Criteria:**
- [ ] App window opens at 1200×800, minimum 900×600, no default menu bar
- [ ] Python sidecar binary spawned with `windowsHide: true` — no console window appears
- [ ] Health poll retries 30 times × 500ms before showing error
- [ ] Splash screen shown during sidecar startup — never a blank window
- [ ] On sidecar ready: renderer loads at correct URL (dev vs packaged)
- [ ] On app-before-quit: `sidecar.kill()` called and confirmed before exit
- [ ] On unexpected sidecar exit: auto-restart triggered, renderer notified via IPC
- [ ] FORGE_DATA_DIR and FORGE_PORT env vars passed to sidecar on spawn
- [ ] All sidecar stderr output written to `{userData}/logs/sidecar.log`

**Key implementation pattern:**
```javascript
// Sidecar path — dev vs packaged
const SIDECAR_PATH = app.isPackaged
  ? path.join(process.resourcesPath, 'sidecar', 'forge_chamber.exe')
  : path.join(__dirname, '..', 'sidecar', 'dist', 'forge_chamber.exe')

// Health poll
function waitForSidecar(retries = 30) {
  return new Promise((resolve, reject) => {
    const check = (n) => {
      http.get(`http://localhost:${PORT}/health`, res => {
        if (res.statusCode === 200) resolve()
        else if (n > 0) setTimeout(() => check(n - 1), 500)
        else reject(new Error('Sidecar timeout'))
      }).on('error', () => {
        if (n > 0) setTimeout(() => check(n - 1), 500)
        else reject(new Error('Sidecar not responding'))
      })
    }
    check(retries)
  })
}
```

**Subtasks:**
- `E2-T1-S1` Window creation — BrowserWindow with correct props, icon, webPreferences — 45m
- `E2-T1-S2` Sidecar path resolution — dev vs packaged logic — 30m
- `E2-T1-S3` Sidecar spawn — child_process.spawn with env, windowsHide, pipe stdio — 45m
- `E2-T1-S4` Health poll — retry loop implementation — 45m
- `E2-T1-S5` Splash screen — splash.html, loadFile on startup, loadURL on ready — 30m
- `E2-T1-S6` Sidecar monitoring — exit handler, auto-restart, IPC notification — 45m
- `E2-T1-S7` Log file management — pipe sidecar stderr to rolling log — 30m

---

### E2-T2 — IPC Bridge & Preload
**Complexity:** M | **Duration:** 2 days

**Description:** Secure contextBridge IPC exposing file system, keychain, and update capabilities to renderer.

**Acceptance Criteria:**
- [ ] `contextIsolation: true` enforced — no direct Node.js access from renderer
- [ ] `window.electronAPI` exposes exactly: pickFiles, readFile, saveApiKeys, getApiKeys, hasApiKeys, onUpdateReady, installUpdate, getSidecarPort
- [ ] pickFiles opens native OS file dialog filtered to pdf, docx, txt, md
- [ ] saveApiKeys writes all 6 keys to OS keychain via electron-keytar
- [ ] hasApiKeys returns boolean — drives onboarding vs dashboard routing

**Subtasks:**
- `E2-T2-S1` preload.js structure — contextBridge.exposeInMainWorld — 30m
- `E2-T2-S2` File system IPC — ipcMain.handle for pick-files and read-file — 45m
- `E2-T2-S3` Keychain IPC — electron-keytar save/get/has for all 6 keys — 45m
- `E2-T2-S4` Update IPC — electron-updater integration — 30m

---

### E2-T3 — Electron Builder Configuration
**Complexity:** L | **Duration:** 2 days

**Description:** electron-builder NSIS config producing signed Windows installer with bundled sidecar.

**Acceptance Criteria:**
- [ ] Produces `Forge-Chamber-Setup-{version}.exe` on `npm run build`
- [ ] NSIS: oneClick install, no directory prompt, per-user, desktop + Start Menu shortcuts
- [ ] extraResources includes sidecar/dist/forge_chamber.exe at correct path
- [ ] publish config points to GitHub Releases (for auto-update URL)
- [ ] Resulting installer file size under 250MB
- [ ] Installed app launches and shows splash within 2 seconds

**package.json build config:**
```json
{
  "build": {
    "appId": "com.ascendion.forge-chamber",
    "productName": "Forge Chamber",
    "win": {
      "target": [{ "target": "nsis", "arch": ["x64"] }]
    },
    "nsis": {
      "oneClick": true,
      "perMachine": false,
      "createDesktopShortcut": true,
      "createStartMenuShortcut": true,
      "shortcutName": "Forge Chamber"
    },
    "extraResources": [
      { "from": "../sidecar/dist/forge_chamber.exe", "to": "sidecar/forge_chamber.exe" }
    ],
    "publish": {
      "provider": "github",
      "owner": "ascendion",
      "repo": "forge-chamber"
    }
  }
}
```

**Subtasks:**
- `E2-T3-S1` Build config in package.json — all settings above — 60m
- `E2-T3-S2` Icon assets — icon.ico (256px), icon.png — 45m
- `E2-T3-S3` Splash screen HTML — branded loading screen, progress animation — 30m
- `E2-T3-S4` Test full build pipeline — sidecar exe + electron installer, verify launch — 90m

---

## EPIC 3 — Python Sidecar & FastAPI Backend
**Timeline:** Weeks 2–3 | **Complexity:** Medium | **Total:** 8 days

### E3-T1 — FastAPI Application Entry Point
**Complexity:** M | **Duration:** 2 days

**Acceptance Criteria:**
- [ ] FastAPI starts on `127.0.0.1:{FORGE_PORT}` — not on network interface
- [ ] CORS configured for localhost only
- [ ] Lifespan: init DB → load embedder → init ChromaDB on startup
- [ ] GET /health returns `{status: "ok", version: "1.0.0"}` within 100ms
- [ ] Unhandled exceptions return structured JSON — never HTML
- [ ] Graceful shutdown on SIGTERM

**main.py structure:**
```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db(DATA_DIR)           # Create SQLite tables
    load_embedder()             # Load sentence-transformers model once
    init_chroma(DATA_DIR)       # Open ChromaDB persistent client
    yield
    # Cleanup on shutdown

app = FastAPI(lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173", "http://localhost:*"])

@app.get("/health")
def health():
    return {"status": "ok", "version": "1.0.0"}
```

**Subtasks:**
- `E3-T1-S1` FastAPI app factory — CORS, lifespan, exception handlers — 60m
- `E3-T1-S2` Config module — pydantic-settings, read all env vars — 30m
- `E3-T1-S3` Route registration — all 5 routers — 20m

---

### E3-T2 — Database Layer (SQLite + SQLAlchemy)
**Complexity:** L | **Duration:** 3 days

**Acceptance Criteria:**
- [ ] SQLite created at `{DATA_DIR}/forge_chamber.db` on first run
- [ ] All 5 tables created with correct schema (engineers, skill_scores, rooms, sessions, turns)
- [ ] SQLAlchemy async engine — non-blocking operations
- [ ] `init_db()` idempotent — safe to call on every startup
- [ ] All CRUD functions have unit tests in tests/test_db.py
- [ ] Foreign key constraints enabled (`PRAGMA foreign_keys = ON`)

**Schema:**
```sql
CREATE TABLE IF NOT EXISTS engineers (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    role_track TEXT NOT NULL,
    skill_level TEXT DEFAULT 'mid',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    total_xp INTEGER DEFAULT 0,
    total_sessions INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS skill_scores (
    id TEXT PRIMARY KEY,
    engineer_id TEXT REFERENCES engineers(id),
    domain TEXT NOT NULL,
    score REAL NOT NULL,
    session_count INTEGER DEFAULT 1,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS rooms (
    id TEXT PRIMARY KEY,
    engineer_id TEXT REFERENCES engineers(id),
    topic TEXT NOT NULL,
    agents TEXT NOT NULL,
    user_role TEXT NOT NULL,
    context_sources TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sessions (
    id TEXT PRIMARY KEY,
    room_id TEXT REFERENCES rooms(id),
    engineer_id TEXT REFERENCES engineers(id),
    started_at DATETIME NOT NULL,
    ended_at DATETIME,
    duration_seconds INTEGER,
    xp_earned INTEGER DEFAULT 0,
    transcript TEXT,
    debrief TEXT,
    technical_depth_score REAL,
    communication_score REAL,
    debate_resilience_score REAL,
    ai_native_score REAL
);

CREATE TABLE IF NOT EXISTS turns (
    id TEXT PRIMARY KEY,
    session_id TEXT REFERENCES sessions(id),
    speaker_type TEXT NOT NULL,
    speaker_key TEXT,
    speaker_name TEXT,
    text TEXT NOT NULL,
    is_quiz_event BOOLEAN DEFAULT FALSE,
    quiz_answered BOOLEAN,
    turn_number INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

**Subtasks:**
- `E3-T2-S1` SQLAlchemy async models — ORM classes for all 5 tables — 90m
- `E3-T2-S2` init_db() — async engine, create_all, PRAGMA foreign_keys — 45m
- `E3-T2-S3` CRUD operations — all create/read/update functions — 120m
- `E3-T2-S4` Unit tests — tests/test_db.py all operations — 60m

---

### E3-T3 — Session API
**Complexity:** L | **Duration:** 3 days

**Acceptance Criteria:**
- [ ] POST /session/start: accepts `{topic, agents, user_role, room_id}`, returns LiveKit URL + token
- [ ] LiveKit token generated with correct room name, identity, grants
- [ ] Session record created in DB before returning token
- [ ] GET /session/{id}: returns full session with transcript and debrief
- [ ] GET /session/list: paginated session list
- [ ] POST /session/{id}/end: accepts transcript, triggers debrief, returns `{debrief, scores, xp_earned}`
- [ ] XP calculation uses formula from functional requirements

**LiveKit token generation:**
```python
from livekit import api

def generate_token(engineer_name: str, room_name: str) -> str:
    token = api.AccessToken(
        os.environ["LIVEKIT_API_KEY"],
        os.environ["LIVEKIT_API_SECRET"]
    )
    token.with_identity(engineer_name)
    token.with_name(engineer_name)
    token.with_grants(api.VideoGrants(
        room_join=True,
        room=room_name,
        can_publish=True,
        can_subscribe=True,
    ))
    return token.to_jwt()
```

---

### E3-T4 — PyInstaller Build Pipeline
**Complexity:** L | **Duration:** 2 days

**Acceptance Criteria:**
- [ ] `pyinstaller forge_chamber.spec` completes without errors on Windows and macOS
- [ ] Output binary runs on a clean machine with no Python installed
- [ ] Binary size under 250MB
- [ ] Startup time from spawn to /health responding under 5 seconds
- [ ] No console window when launched from Electron (console=False)

**forge_chamber.spec:**
```python
from PyInstaller.utils.hooks import collect_all

datas, binaries, hiddenimports = [], [], []
for pkg in ['sentence_transformers', 'chromadb', 'llama_index',
            'livekit', 'fastapi', 'uvicorn', 'langchain', 'langgraph']:
    d, b, h = collect_all(pkg)
    datas += d; binaries += b; hiddenimports += h

a = Analysis(['main.py'], datas=datas, binaries=binaries,
             hiddenimports=hiddenimports)
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, a.binaries, a.datas,
          name='forge_chamber', console=False, onefile=True)
```

---

## EPIC 4 — Voice Pipeline Integration
**Timeline:** Weeks 3–4 | **Complexity:** High | **Total:** 8 days

### E4-T1 — LiveKit Worker Process
**Complexity:** L | **Duration:** 3 days

**Acceptance Criteria:**
- [ ] Worker connects to LiveKit Cloud on startup with correct credentials
- [ ] Worker receives job within 2 seconds of POST /session/start
- [ ] Single VoiceAssistant created with Deepgram STT (nova-2), Silero VAD, Cartesia TTS, Claude LLM
- [ ] VAD detects speech start within 300ms of user speaking
- [ ] STT produces transcript within 500ms of speech end
- [ ] TTS audio starts streaming within 2 seconds of LLM response start
- [ ] `python voice/livekit_worker.py dev` starts without error

**Core worker pattern:**
```python
from livekit.agents import AutoSubscribe, JobContext, WorkerOptions, cli
from livekit.agents.voice_assistant import VoiceAssistant
from livekit.plugins import anthropic, deepgram, silero, cartesia

async def entrypoint(ctx: JobContext):
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)
    
    assistant = VoiceAssistant(
        vad=silero.VAD.load(),
        stt=deepgram.STT(model="nova-2", smart_format=True),
        llm=anthropic.LLM(model="claude-sonnet-4-5"),
        tts=cartesia.TTS(voice=PERSONAS[active_persona]["voice_id"]),
        chat_ctx=build_chat_context(active_persona, rag_context),
    )
    assistant.start(ctx.room)
    await assistant.say("Welcome to Forge Chamber. " + PERSONAS[active_persona]["greeting"])
    await asyncio.sleep(7200)

if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
```

---

### E4-T2 — Multi-Voice TTS Routing
**Complexity:** M | **Duration:** 1 day

**Acceptance Criteria:**
- [ ] VOICE_IDS maps all 5 agent keys to distinct Cartesia voice IDs
- [ ] Each agent voice is clearly distinguishable in listening test
- [ ] Voice switching works when persona changes mid-session

**Voice ID mapping:**
```python
VOICE_IDS = {
    "sre":       "694f9389-aac1-45b6-b726-9d9369183238",  # Deep male
    "sys_arch":  "a0e99841-438c-4a64-b679-ae501e7d6091",  # Warm female
    "cloud_eng": "63ff761f-c1e8-414b-b969-d1833d1c870c",  # Neutral male
    "java_dev":  "b7d50908-b17c-442d-ad8d-810c63997ed9",  # Crisp male
    "ui_dev":    "156fb8d2-335b-4950-9cb3-a2d33befec77",  # Energetic
}
```

---

### E4-T3 — Human Interrupt & Transcript Channel
**Complexity:** L | **Duration:** 4 days

**Acceptance Criteria:**
- [ ] User speech stops agent TTS within 200ms (LiveKit allow_interruptions)
- [ ] `user_speech_committed` event fires after speech ends
- [ ] Agents resume within 2 seconds of human finishing
- [ ] After each agent utterance: publish `{type: "turn_committed", speaker_key, speaker_name, text, turn_number}`
- [ ] Speaker changes publish: `{type: "speaker_change", agent_key, agent_name, agent_role}`
- [ ] Quiz events publish: `{type: "quiz_event", question, agent_key, timeout_seconds: 30}`

```python
# Data channel publisher helper
async def publish_turn(room, speaker_key, name, role, text, turn_num):
    msg = json.dumps({
        "type": "turn_committed",
        "speaker_key": speaker_key,
        "speaker_name": name,
        "speaker_role": role,
        "text": text,
        "turn_number": turn_num,
    })
    await room.local_participant.publish_data(msg.encode(), reliable=True)
```

---

## EPIC 5 — Multi-Agent Debate Engine
**Timeline:** Weeks 4–6 | **Complexity:** Very High | **Total:** 12 days

### E5-T1 — Agent Persona Definitions
**Complexity:** L | **Duration:** 3 days

**Acceptance Criteria:**
- [ ] PERSONAS dict contains all 5 agents with complete configuration
- [ ] Each system prompt follows template from CLAUDE.md exactly
- [ ] Every prompt contains Socratic obligation (end every turn with a question)
- [ ] Turn length constraint in every prompt: "2–4 sentences maximum"
- [ ] Each agent has minimum 7 disagreement trigger topics
- [ ] Manual test: each agent gives distinct, in-character responses to "microservices API design"

**Persona template:**
```python
PERSONAS = {
    "sre": {
        "name": "Alex",
        "role": "SRE",
        "voice_id": "694f9389-aac1-45b6-b726-9d9369183238",
        "color": "#E8533A",
        "greeting": "SRE here. What are you building — and what breaks first?",
        "system": """You are Alex, SRE, in a live engineering debate panel in Forge Chamber.
You are speaking TO OTHER ENGINEERS ON THE PANEL, not to the student.
The student engineer is listening and may jump in at any time.
If the student has not spoken for 5+ turns, you MUST address them directly.

YOUR MANDATE: Production reliability, observability, SLOs, blast radius, incident response, runbooks.

YOUR STYLE: Direct, slightly combative, always concrete. Cite real incident patterns.
Never accept "we'll fix it later."

YOUR TRIGGER POINTS (always push back on):
- Vague or missing SLOs
- No monitoring or alerting strategy
- Missing circuit breakers
- Untested rollback procedure
- Undefined blast radius
- Logging gaps
- No runbook defined

DEBATE RULES:
- 2–4 sentences maximum per turn
- React DIRECTLY to what was just said — no summaries
- End EVERY turn with a failure-mode question
- Address agents by name when challenging directly

Current topic: {topic}
{rag_context}

Recent debate:
{transcript_last_8}""",
        "quiz_topics": ["SLO definition", "blast radius", "runbook contents", 
                       "circuit breaker pattern", "mean time to recovery"],
        "disagreement_triggers": ["missing monitoring", "no rollback plan", 
                                  "vague SLO", "untested deployment"],
    },
    # ... sys_arch, cloud_eng, java_dev, ui_dev follow same pattern
}
```

---

### E5-T2 — LangGraph Debate Orchestrator
**Complexity:** XL | **Duration:** 5 days

**Acceptance Criteria:**
- [ ] DebateState TypedDict with all required fields
- [ ] StateGraph with 5 nodes: route_turn, generate_turn, detect_quiz, wait_for_human, resume_debate
- [ ] route_turn calls Claude Haiku, returns valid JSON `{next_speaker, seed, tension_target}`
- [ ] route_turn falls back to round-robin on invalid JSON
- [ ] generate_turn calls Claude Sonnet with agent system prompt + last 8 turns
- [ ] detect_quiz triggers when `human_silent_turns >= 5`
- [ ] No agent speaks twice consecutively unless directly challenged
- [ ] Integration test: 3-agent debate runs 15 turns without error

**LangGraph structure:**
```python
from langgraph.graph import StateGraph, END
from typing import TypedDict, Optional

class DebateState(TypedDict):
    topic: str
    agents: list[str]
    transcript: list[dict]
    turn_count: int
    active_speaker: Optional[str]
    human_silent_turns: int
    is_paused: bool
    rag_context: str
    session_id: str

ORCHESTRATOR_SYSTEM = """You manage turn-taking in an engineering debate.
Respond ONLY with valid JSON:
{
  "next_speaker": "sre|sys_arch|cloud_eng|java_dev|ui_dev",
  "seed": "one-sentence prompt for that agent to react to",
  "tension_target": "agent_key or null"
}
Rules: never same agent twice; increase tension after 3 agreeable turns;
if an agent was named in last utterance, they respond next."""

async def route_turn(state: DebateState) -> DebateState:
    response = await claude_haiku.messages.create(
        model="claude-haiku-4-5",
        max_tokens=150,
        system=ORCHESTRATOR_SYSTEM,
        messages=[{"role": "user", "content": format_transcript(state)}]
    )
    try:
        decision = json.loads(response.content[0].text)
        state["active_speaker"] = decision["next_speaker"]
        state["current_seed"] = decision["seed"]
    except:
        # Round-robin fallback
        last = state["transcript"][-1]["speaker_key"] if state["transcript"] else None
        available = [a for a in state["agents"] if a != last]
        state["active_speaker"] = available[0]
    return state

# Build graph
graph = StateGraph(DebateState)
graph.add_node("route_turn", route_turn)
graph.add_node("generate_turn", generate_turn)
graph.add_node("detect_quiz", detect_quiz)
graph.add_node("wait_for_human", wait_for_human)
graph.add_node("resume_debate", resume_debate)

graph.add_edge("route_turn", "generate_turn")
graph.add_edge("generate_turn", "detect_quiz")
graph.add_conditional_edges("detect_quiz", 
    lambda s: "wait_for_human" if s["human_silent_turns"] >= 5 else "route_turn")
graph.add_edge("wait_for_human", "resume_debate")
graph.add_edge("resume_debate", "route_turn")
graph.set_entry_point("route_turn")
debate_graph = graph.compile()
```

---

### E5-T3 — Quiz & Socratic Mechanics
**Complexity:** L | **Duration:** 3 days

**Acceptance Criteria:**
- [ ] Quiz event fires when `human_silent_turns >= 5`
- [ ] Data channel publishes quiz_event with question and 30-second timeout
- [ ] If user silent 30s: agent answers the question with detailed explanation
- [ ] After unanswered quiz: "I'll come back to this" then return within 3 turns
- [ ] If user responds: agents acknowledge and continue debate

---

### E5-T4 — Post-Session Debrief Generator
**Complexity:** L | **Duration:** 3 days

**Acceptance Criteria:**
- [ ] `synthesize_session()` accepts full transcript list, returns structured debrief
- [ ] Claude Sonnet called with debrief system prompt
- [ ] Response parsed as valid JSON — retry once, default scores if fail
- [ ] Debrief contains: key_insights(3), strong_moments(2-3), knowledge_gaps(2-3), scores(4), overall_comment
- [ ] All scores are floats 1.0–5.0
- [ ] XP calculated per formula: base 50 + complexity × participation

**Debrief system prompt:**
```
Analyze this engineering debate transcript. 
Respond ONLY with valid JSON:
{
  "key_insights": ["...", "...", "..."],
  "strong_moments": [{"turn": N, "observation": "..."}],
  "knowledge_gaps": [{"topic": "...", "suggested_study": "..."}],
  "scores": {
    "technical_depth": 1-5,
    "communication": 1-5,
    "debate_resilience": 1-5,
    "ai_native": 1-5
  },
  "overall_comment": "..."
}
Rubric: 1=no engagement, 2=significant gaps, 3=competent, 4=strong, 5=exceptional
```

---

## EPIC 6 — RAG Pipeline & Context Ingestion
**Timeline:** Weeks 6–7 | **Complexity:** High | **Total:** 7 days

### E6-T1 — Document Ingestion Pipeline
**Complexity:** L | **Duration:** 3 days

**Acceptance Criteria:**
- [ ] POST /rag/ingest-url: returns `{status, chunks, title}` within 10 seconds
- [ ] POST /rag/ingest-file: handles PDF, DOCX, TXT, MD correctly
- [ ] SentenceSplitter: 500 tokens, 50 overlap
- [ ] sentence-transformers embeds locally within 5s for 50 chunks
- [ ] ChromaDB upsert: duplicate URLs update existing chunks
- [ ] sources.json updated after each ingest

**Ingestion pattern:**
```python
from llama_index.readers.web import SimpleWebPageReader
from llama_index.core.node_parser import SentenceSplitter
import chromadb
from sentence_transformers import SentenceTransformer

# Load once at startup
EMBEDDER = SentenceTransformer('all-MiniLM-L6-v2')
CHROMA = chromadb.PersistentClient(path=f"{DATA_DIR}/chroma")
COLLECTION = CHROMA.get_or_create_collection("forge_context")

def ingest_url(url: str) -> dict:
    docs = SimpleWebPageReader(html_to_text=True).load_data([url])
    splitter = SentenceSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_text(docs[0].text)
    embeddings = EMBEDDER.encode(chunks).tolist()
    
    ids = [f"{url}:{i}" for i in range(len(chunks))]
    COLLECTION.upsert(ids=ids, documents=chunks, embeddings=embeddings,
                      metadatas=[{"source": url} for _ in chunks])
    return {"chunks": len(chunks), "title": url}
```

---

### E6-T2 — Context Retrieval & Injection
**Complexity:** M | **Duration:** 2 days

**Acceptance Criteria:**
- [ ] `retrieve_context(query, n=4)` returns formatted context block
- [ ] Query built from last 2 utterances concatenated
- [ ] Returns empty string if collection empty — no error
- [ ] Retrieval adds < 200ms to agent turn generation time
- [ ] Context formatted with `[From: {source}]` headers

```python
def retrieve_context(query: str, n: int = 4) -> str:
    if COLLECTION.count() == 0:
        return ""
    results = COLLECTION.query(query_texts=[query], n_results=min(n, COLLECTION.count()))
    chunks = results["documents"][0]
    sources = [m["source"] for m in results["metadatas"][0]]
    
    parts = [f"[From: {src}]\n{chunk}" for chunk, src in zip(chunks, sources)]
    return "\n\n---\n\n".join(parts)
```

---

## EPIC 7 — React UI Implementation
**Timeline:** Weeks 5–8 | **Complexity:** High | **Total:** 14 days

### E7-T1 — App Shell & Routing
**Complexity:** M | **Duration:** 2 days

**Acceptance Criteria:**
- [ ] React Router v6 with routes for all 7 pages
- [ ] Zustand store: engineer, room, session, settings slices
- [ ] On startup: check `electronAPI.hasApiKeys()` → route to Onboarding or Dashboard
- [ ] Global CSS variables per design.md (dark mode default)
- [ ] API client: typed fetch, base URL http://localhost:8765, error handling

**CSS Variables (global.css):**
```css
:root {
  --brand: #2B5EA7;
  --accent: #E8533A;
  --surface: #0F0F14;
  --surface-2: #1A1A24;
  --surface-3: #252535;
  --text-1: #F0EEF8;
  --text-2: #9A99B0;
  --text-3: #55546A;
  --border: rgba(255,255,255,0.10);
  --agent-sre: #E8533A;
  --agent-arch: #4A7CC7;
  --agent-cloud: #1D9E75;
  --agent-java: #D4890A;
  --agent-ui: #8B7FE8;
  --agent-human: #3AAA5A;
  --radius-sm: 6px;
  --radius-md: 10px;
  --radius-lg: 14px;
}
```

---

### E7-T2 through E7-T6 — All UI Screens

**E7-T2: Onboarding Screen** (M, 2d)
- Two-column: brand left + form right
- Name, role dropdown, skill level radio
- 6 API key inputs with show/hide toggles
- Submit: save to keychain + POST /engineer/setup + navigate

**E7-T3: Dashboard** (L, 3d)
- XP counter header, topic input, curated topic pills
- Agent selection pills (toggle), 2-agent minimum validation
- Recent sessions list with skeleton loading

**E7-T4: Room Active** (XL, 5d) ← Most complex
- LiveKit room connection with token
- Data channel: parse turn_committed, speaker_change, quiz_event
- TranscriptFeed: auto-scroll, turn cards per agent color
- VoiceBar: animated waveform, speaker name, Join/Leave toggle
- AgentPanel: animated ring on active speaker
- Quiz zone: amber card with 30s countdown

**E7-T5: Debrief & Progress** (L, 3d)
- Debrief: XP animation, 4 score cards with delta, SkillRadar SVG
- Progress: longitudinal radar, domain bars, session history table

**E7-T6: ContextDrop** (M, 2d)
- URL input with Enter-to-submit
- File drag-and-drop + electronAPI.pickFiles
- Source chips with chunk count + delete
- Notify LiveKit worker after ingest

**SkillRadar SVG (pure, no library):**
```tsx
const SkillRadar = ({ scores }: { scores: SkillScores }) => {
  const cx = 150, cy = 150, r = 110
  const axes = ['technical_depth', 'communication', 'debate_resilience', 'ai_native']
  const labels = ['Technical', 'Communication', 'Resilience', 'AI-Native']
  
  const point = (i: number, score: number) => {
    const angle = (i * Math.PI * 2) / axes.length - Math.PI / 2
    const dist = (score / 5) * r
    return { x: cx + dist * Math.cos(angle), y: cy + dist * Math.sin(angle) }
  }
  
  const polygonPoints = axes.map((a, i) => {
    const p = point(i, scores[a] ?? 1)
    return `${p.x},${p.y}`
  }).join(' ')
  
  return (
    <svg width="300" height="300" viewBox="0 0 300 300">
      {/* Grid circles */}
      {[1,2,3,4,5].map(level => (
        <circle key={level} cx={cx} cy={cy} r={(level/5)*r}
          fill="none" stroke="var(--border)" strokeWidth="0.5"/>
      ))}
      {/* Score polygon */}
      <polygon points={polygonPoints}
        fill="var(--brand)" fillOpacity="0.25"
        stroke="var(--brand)" strokeWidth="2"/>
      {/* Axis labels */}
      {axes.map((a, i) => {
        const p = point(i, 5.4)
        return <text key={a} x={p.x} y={p.y} textAnchor="middle"
          dominantBaseline="central" fontSize="11" fill="var(--text-2)">{labels[i]}</text>
      })}
    </svg>
  )
}
```

---

## EPIC 8 — Skills, XP & Progress Tracking
**Timeline:** Weeks 8–9 | **Complexity:** Medium | **Total:** 6 days

### E8-T1 — Skills Scoring Engine (M, 3d)

**Acceptance Criteria:**
- [ ] 4 domains scored per session: technical_depth, communication, debate_resilience, ai_native
- [ ] First session: stored as baseline
- [ ] Subsequent: rolling weighted average (70% historical, 30% new)
- [ ] Score floor: cannot decrease by more than 0.5 in single session
- [ ] GET /progress/skills returns current averages
- [ ] GET /progress/sessions returns per-session history

### E8-T2 — XP System (S, 1d)

**XP Formula:**
```python
def calculate_xp(session: Session, transcript: list[Turn]) -> dict:
    base = 50
    human_turns = len([t for t in transcript if t.speaker_type == "human"])
    quiz_answered = len([t for t in transcript if t.is_quiz_event and t.quiz_answered])
    quiz_partial = len([t for t in transcript if t.is_quiz_event and not t.quiz_answered])
    duration_min = session.duration_seconds / 60
    streak = get_current_streak(session.engineer_id)
    
    xp = base
    xp += human_turns * 10
    xp += quiz_answered * 15
    xp += quiz_partial * 5
    if duration_min >= 15: xp += 20
    if streak > 1: xp += min(streak, 7) * 10
    
    return {"total": xp, "breakdown": {
        "base": base, "participation": human_turns * 10,
        "quiz_answered": quiz_answered * 15, "duration_bonus": 20 if duration_min >= 15 else 0,
        "streak": min(streak, 7) * 10
    }}
```

---

## EPIC 9 — Testing & Quality Assurance
**Timeline:** Weeks 9–10 | **Complexity:** Medium | **Total:** 8 days

### E9-T1 — Python Sidecar Tests (L, 4d)

**Acceptance Criteria:**
- [ ] `pytest sidecar/tests/ -v` runs with 0 failures
- [ ] test_db.py: CRUD for all 5 tables, FK constraints
- [ ] test_rag.py: URL ingest (mocked HTTP), file ingest, retrieval
- [ ] test_personas.py: each persona generates non-empty string ending with "?"
- [ ] test_debrief.py: synthesize_session() returns valid JSON
- [ ] test_api.py: all route happy paths via httpx TestClient
- [ ] LLM calls mocked — no real API calls in test suite
- [ ] Overall coverage >= 80%

**Mock pattern:**
```python
# tests/conftest.py
import pytest
from unittest.mock import AsyncMock, patch

@pytest.fixture
def mock_claude():
    with patch('anthropic.AsyncAnthropic') as mock:
        mock.return_value.messages.create = AsyncMock(return_value=MockResponse(
            content=[MockContent(text='Alex: What is your SLO? End with a question?')]
        ))
        yield mock

@pytest.fixture
def test_chroma(tmp_path):
    import chromadb
    return chromadb.EphemeralClient()  # In-memory for tests
```

### E9-T2 — React Component Tests (M, 2d)

**Acceptance Criteria:**
- [ ] `npx vitest run` passes with 0 failures
- [ ] VoiceBar.test.tsx: 3 states (listen/active/processing)
- [ ] TranscriptFeed.test.tsx: turn rendering, auto-scroll, colors
- [ ] SkillRadar.test.tsx: correct polygon shape for score data
- [ ] ContextDrop.test.tsx: URL submit, file picker, source chips

### E9-T3 — End-to-End Manual Test (M, 2d)

Documented test script covering: install → onboarding → create room → ingest URL → 5-turn debate → end → debrief. Must pass on clean Windows 11 machine.

---

## EPIC 10 — CI/CD Pipeline & Distribution
**Timeline:** Weeks 10–12 | **Complexity:** High | **Total:** 10 days

### CI/CD Architecture

```
Developer pushes code
         │
         ▼
  .github/workflows/ci.yml  (every push/PR)
  ├── python-tests job       (pytest, coverage)
  └── react-tests job        (vitest, tsc)
         │
         ▼ (if tag v*.*.*)
  .github/workflows/release.yml
  ├── Python 3.11 + VS Build Tools
  ├── pyinstaller forge_chamber.spec
  ├── npm run build (renderer)
  ├── electron-builder --win --x64
  └── Upload .exe to GitHub Releases
         │
         ▼
  .github/workflows/pages.yml  (on release published)
  └── Update download page version
```

### E10-T1 — Continuous Integration (M, 2d)

**.github/workflows/ci.yml:**
```yaml
name: CI
on:
  push:
    branches: ["**"]
  pull_request:
    branches: [main, develop]

jobs:
  python-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11.9"
          cache: pip
      - run: |
          cd sidecar
          pip install -r requirements.txt pytest pytest-cov httpx
          pytest tests/ -v --cov=. --cov-fail-under=80
        env:
          FORGE_DATA_DIR: /tmp/forge-test
          FORGE_PORT: 8765
          ANTHROPIC_API_KEY: test-key-not-real
          LIVEKIT_URL: wss://test.livekit.cloud
          LIVEKIT_API_KEY: test-key
          LIVEKIT_API_SECRET: test-secret

  react-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: "20"
          cache: npm
          cache-dependency-path: renderer/package-lock.json
      - run: cd renderer && npm ci && npx vitest run
      - run: cd renderer && npx tsc --noEmit
```

**Acceptance Criteria:**
- [ ] CI triggers on push to any branch and PR to main
- [ ] Both jobs must pass for PR to be mergeable
- [ ] Coverage report uploaded as artifact
- [ ] Full CI run completes under 5 minutes

### E10-T2 — Release Build Pipeline (XL, 5d)

**.github/workflows/release.yml:**
```yaml
name: Release Build
on:
  push:
    tags:
      - "v*.*.*"

permissions:
  contents: write

jobs:
  build-windows:
    runs-on: windows-latest
    timeout-minutes: 45
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - uses: actions/setup-python@v5
        with:
          python-version: "3.11.9"

      - name: Install VS Build Tools
        run: |
          choco install vcredist140 -y
          choco install visualstudio2022buildtools --package-parameters "--add Microsoft.VisualStudio.Workload.VCTools" -y

      - name: Build Python sidecar
        run: |
          cd sidecar
          pip install -r requirements.txt pyinstaller
          pyinstaller forge_chamber.spec

      - uses: actions/setup-node@v4
        with:
          node-version: "20"

      - name: Build renderer
        run: cd renderer && npm ci && npm run build

      - name: Build Electron installer
        run: cd electron && npm ci && npx electron-builder --win --x64 --publish never

      - name: Create GitHub Release
        uses: softprops/action-gh-release@v1
        with:
          files: electron/dist/*.exe
          generate_release_notes: true
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

**Acceptance Criteria:**
- [ ] Tag push triggers build automatically
- [ ] Full pipeline under 20 minutes
- [ ] .exe uploaded to GitHub Releases
- [ ] electron-updater can find and download the release
- [ ] No secrets in CI logs

### E10-T3 — Download Page (S, 1d)

Static HTML page deployed to GitHub Pages. "Download for Windows" links to latest release. Version auto-updates from GitHub API.

### E10-T4 — Secrets & Security (M, 2d)

**Required GitHub Secrets:**

| Secret | Source | Used By |
|--------|--------|---------|
| GITHUB_TOKEN | Auto-provided | release.yml — publish |
| CSC_LINK | IT org certificate | Optional code signing |
| CSC_KEY_PASSWORD | Certificate password | Optional code signing |

**Pre-commit hook (blocks accidental secret commits):**
```bash
#!/bin/bash
if git diff --cached | grep -E 'sk-ant-|AKIA|\.livekit\.cloud/keys'; then
  echo "ERROR: Possible secret detected in staged files"
  exit 1
fi
```

---

## Section 5: CI/CD Pipeline

### Branch Strategy

| Branch | Purpose | Protection | Merge Policy |
|--------|---------|------------|--------------|
| main | Production releases | Require PR + CI + 1 review | Squash merge |
| develop | Integration | Require CI | Merge commit |
| feature/* | Feature work | None | PR to develop |
| fix/* | Bug fixes | None | PR to develop/main |
| release/* | Release prep | Require CI | PR to main + tag |

### Release Process

```bash
# 1. Merge develop → main via PR
# 2. Tag main
git checkout main && git pull
git tag -a v1.0.0 -m "Forge Chamber v1.0.0 — Initial release"
git push origin v1.0.0
# GitHub Actions triggers automatically
```

### Versioning (Semantic)

- **MAJOR:** Breaking changes to session format, agent API, installer
- **MINOR:** New features (persona, context type, UI screen)
- **PATCH:** Bug fixes, performance, security

---

## Section 6: Process & Workflow

### Sprint Structure (2-week sprints)

| Sprint | EPICs | Goal |
|--------|-------|------|
| S1 (W1–2) | E1 + E2 + E3 start | App launches, sidecar responds to /health |
| S2 (W3–4) | E3 finish + E4 | Single-agent voice conversation working |
| S3 (W5–6) | E5 + E7 start | Multi-agent debate runs; basic UI navigable |
| S4 (W7–8) | E6 + E7 finish + E8 | URL context; full UI; skills tracking live |
| S5 (W9–10) | E9 + E10 start | All tests passing; CI green; release build works |
| S6 (W11–12) | E10 finish + pilot | Installer downloadable; 5-engineer pilot |

### Definition of Done (per task)

- [ ] All acceptance criteria in task card verified manually
- [ ] Code committed to feature branch with descriptive commit messages
- [ ] Unit tests written and passing for new functionality
- [ ] No TypeScript type errors (`tsc --noEmit` passes)
- [ ] PR opened against develop with task ID in title e.g. `[E3-T2] Database layer`
- [ ] CI pipeline green on PR
- [ ] No commented-out code, no `console.log`, no TODO without ticket

### Commit Message Convention

```
[TYPE](scope): description

Types: feat, fix, test, docs, refactor, chore
Scope: electron, sidecar, renderer, ci, rag, agents

Examples:
feat(sidecar): implement LangGraph debate orchestrator (E5-T2)
fix(renderer): transcript feed not auto-scrolling (E7-T4)
test(sidecar): add pytest coverage for RAG pipeline (E9-T1)
chore(ci): add PyInstaller build step to release.yml (E10-T2)
```

---

## Section 7: Observability & Operations

### Log Files

| File | Location (Windows) | Contents |
|------|--------------------|---------|
| sidecar.log | %APPDATA%\ForgeChamber\logs\ | FastAPI startup, requests, errors |
| worker.log | %APPDATA%\ForgeChamber\logs\ | LiveKit worker, debate turns |
| electron.log | %APPDATA%\ForgeChamber\logs\ | App lifecycle, IPC, updates |

### Data Directory Contents

```
%APPDATA%\ForgeChamber\
├── forge_chamber.db      # SQLite — all sessions, skills, XP
├── chroma/               # ChromaDB vector store
├── sources.json          # Ingested context sources index
├── engineer_id.txt       # Persistent engineer UUID
├── logs/
│   ├── sidecar.log
│   ├── worker.log
│   └── electron.log
└── tmp/                  # Uploaded files (transient)
```

### Common Issues & Resolutions

| Issue | Symptom | Resolution |
|-------|---------|------------|
| Sidecar not starting | Splash hangs > 10s | Check logs/sidecar.log — usually port 8765 in use |
| VAD not detecting speech | Transcript empty | Check Deepgram API key, mic permissions in Windows Privacy |
| Agents not responding | Timer advances, no audio | Check ANTHROPIC_API_KEY, verify Claude API quota |
| TTS silent | Transcript shows but no audio | Check CARTESIA_API_KEY, verify OS speaker volume |
| ChromaDB import error | Sidecar crash | Delete data/chroma/, rebuild on restart |
| PyInstaller missing module | Exe crash on clean machine | Add to hiddenimports in .spec, rebuild |

### Diagnostic Commands

```bash
# Health check
curl http://localhost:8765/health

# DB size
python -c "import os; print(os.path.getsize('data/forge_chamber.db'))"

# ChromaDB chunk count
python -c "
import chromadb
c = chromadb.PersistentClient('data/chroma')
col = c.get_collection('forge_context')
print('Chunks:', col.count())
"

# All tests verbose
pytest sidecar/tests/ -v -s

# Windows: find orphaned sidecar
Get-Process | Where-Object { $_.Name -eq "forge_chamber" }
```

---

## Section 8: Reference

### API Keys Quick Setup

| Service | URL | Free Tier |
|---------|-----|-----------|
| Anthropic | console.anthropic.com | $5 credit on signup |
| LiveKit | livekit.io/cloud | 1000 agent mins + 5000 participant mins/month |
| Deepgram | deepgram.com | $200 credit on signup (~46,000 mins) |
| Cartesia | cartesia.ai | Free tier available |

### Technology Versions

| Technology | Version | Pin Reason |
|------------|---------|------------|
| Python | 3.11.9 | LiveKit plugin compatibility |
| Node.js | 20 LTS | Electron 28 requirement |
| Electron | 28.x | Windows 11 support |
| FastAPI | 0.111.0 | Async lifespan, Pydantic v2 |
| livekit-agents | 0.8.7 | Multi-agent pipeline stable |
| langchain | 0.2.12 | LangGraph 0.1.x compatibility |
| chromadb | 0.5.11 | Embedded mode stable |
| sentence-transformers | 3.0.1 | all-MiniLM-L6-v2 available, CPU-friendly |
| PyInstaller | 6.9.0 | Windows one-file mode stable |

### Quick Commands Reference

```bash
# Dev startup (4 terminals)
cd sidecar && source .venv/bin/activate && python main.py
cd sidecar && source .venv/bin/activate && python voice/livekit_worker.py dev
cd renderer && npm run dev
cd electron && RENDERER_URL=http://localhost:5173 npm run dev

# Build sidecar exe
cd sidecar && pyinstaller forge_chamber.spec

# Build electron installer
cd electron && npm run build

# Run all tests
cd sidecar && pytest tests/ -v
cd renderer && npx vitest run

# Type check
cd renderer && npx tsc --noEmit

# Release tag
git tag -a v1.0.0 -m "Forge Chamber v1.0.0"
git push origin v1.0.0
```

---

*Forge Chamber — Detailed Development Guide v1.0*  
*Ascendion Digital Services Philippines Inc. | Forge Engineering Excellence Program*  
*Author: Jeril John Panicker, Solutions Architect*
