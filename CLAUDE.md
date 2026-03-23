# CLAUDE.md — Forge Chamber Build Specification

> This file is the authoritative specification for building Forge Chamber.
> It is written for Claude Code. Follow every section precisely.
> When in doubt: prefer simplicity, prefer explicitness, prefer correctness over cleverness.

---

## Project Identity

**App name:** Forge Chamber  
**Tagline:** Where engineers get tested  
**Type:** Standalone Electron desktop app (Windows-first, macOS Phase 2)  
**Distribution:** Single installer download, like Claude Desktop  
**Backend:** Bundled Python sidecar (FastAPI + LiveKit Agents)  
**Primary user:** Software engineers at Ascendion Digital Services  

---

## Repository Structure

Build the following directory structure exactly:

```
forge-chamber/
├── electron/                        # Electron main process
│   ├── main.js                      # App lifecycle, sidecar management, IPC
│   ├── preload.js                   # Secure IPC bridge to renderer
│   ├── splash.html                  # Loading screen while sidecar starts
│   ├── assets/
│   │   ├── icon.ico                 # Windows app icon
│   │   └── icon.png                 # Linux/macOS icon
│   └── package.json                 # Electron + electron-builder config
│
├── renderer/                        # React frontend (Vite)
│   ├── src/
│   │   ├── App.tsx                  # Root component, routing
│   │   ├── main.tsx                 # Vite entry point
│   │   ├── pages/
│   │   │   ├── Onboarding.tsx       # First-launch setup
│   │   │   ├── Dashboard.tsx        # Home — sessions, profile, new room
│   │   │   ├── RoomSetup.tsx        # Configure topic, agents, context
│   │   │   ├── RoomActive.tsx       # Live debate session view
│   │   │   ├── Debrief.tsx          # Post-session summary
│   │   │   └── Progress.tsx         # Skill radar, XP, session history
│   │   ├── components/
│   │   │   ├── VoiceBar.tsx         # Live waveform + speaker indicator
│   │   │   ├── TranscriptFeed.tsx   # Scrolling real-time transcript
│   │   │   ├── AgentPanel.tsx       # Agent cards showing active/idle state
│   │   │   ├── ContextDrop.tsx      # URL paste + file upload zone
│   │   │   ├── PersonaCard.tsx      # Agent selection card
│   │   │   ├── SkillRadar.tsx       # SVG radar chart (no external chart lib)
│   │   │   ├── XPBar.tsx            # XP progress bar with animation
│   │   │   ├── DebriefCard.tsx      # Structured session debrief display
│   │   │   └── UpdateBanner.tsx     # App update notification
│   │   ├── hooks/
│   │   │   ├── useRoom.ts           # Room lifecycle management
│   │   │   ├── useVoice.ts          # Microphone, VAD, push-to-talk
│   │   │   ├── useTranscript.ts     # Real-time transcript state
│   │   │   └── useSession.ts        # Session persistence and retrieval
│   │   ├── store/
│   │   │   └── app.ts               # Zustand global state
│   │   ├── lib/
│   │   │   ├── api.ts               # Typed fetch client → FastAPI sidecar
│   │   │   └── constants.ts         # Agent definitions, color maps, routes
│   │   └── styles/
│   │       └── global.css           # CSS variables, reset, typography
│   ├── index.html
│   ├── vite.config.ts
│   ├── tsconfig.json
│   └── package.json
│
├── sidecar/                         # Python backend (bundled via PyInstaller)
│   ├── main.py                      # FastAPI app + LiveKit worker entry
│   ├── api/
│   │   ├── routes/
│   │   │   ├── health.py            # GET /health
│   │   │   ├── session.py           # POST /session/start, GET /session/{id}
│   │   │   ├── rag.py               # POST /rag/ingest-url, /rag/ingest-file
│   │   │   ├── engineer.py          # GET/POST /engineer profile
│   │   │   └── progress.py          # GET /progress/skills, /progress/sessions
│   │   └── models.py                # Pydantic request/response schemas
│   ├── agents/
│   │   ├── orchestrator.py          # LangGraph debate turn orchestrator
│   │   ├── personas.py              # All 5 agent persona definitions
│   │   ├── debate_engine.py         # Autonomous debate loop + human interrupt
│   │   └── synthesizer.py           # Post-session debrief + skill scoring
│   ├── voice/
│   │   ├── livekit_worker.py        # LiveKit agent worker process
│   │   └── tts_router.py            # Cartesia TTS with voice-per-agent
│   ├── rag/
│   │   ├── ingester.py              # LlamaIndex URL + file ingestion
│   │   ├── retriever.py             # ChromaDB semantic search
│   │   └── embedder.py              # sentence-transformers local embedding
│   ├── db/
│   │   ├── database.py              # SQLite connection + init
│   │   ├── models.py                # SQLAlchemy ORM models
│   │   └── crud.py                  # DB operations
│   ├── core/
│   │   ├── config.py                # Environment config (pydantic-settings)
│   │   └── logging.py               # Structured logging setup
│   ├── requirements.txt
│   ├── forge_chamber.spec           # PyInstaller build spec
│   └── build.sh                     # Build script: pip install + pyinstaller
│
├── scripts/
│   ├── build-all.sh                 # Full build: sidecar → renderer → electron
│   └── dev.sh                       # Start all services in dev mode
│
├── .env.example                     # Template for required environment variables
├── .gitignore
└── README.md
```

---

## Technology Stack

### Electron Shell
- **Electron:** 28.x (current LTS)
- **electron-builder:** 24.x — produces NSIS installer for Windows
- **electron-updater:** auto-update via GitHub Releases
- **electron-keytar:** secure keychain storage for API keys

### Renderer (React UI)
- **React:** 18.x with TypeScript
- **Vite:** 5.x — dev server and production build
- **Zustand:** 4.x — global state (engineer profile, active room, session)
- **@livekit/components-react:** LiveKit React SDK for voice room
- **livekit-client:** LiveKit JS client
- **TailwindCSS:** 3.x — utility-first styling
- **No heavy chart libraries** — implement SkillRadar as inline SVG

### Python Sidecar
- **Python:** 3.11.x
- **FastAPI:** 0.111.x with uvicorn
- **livekit-agents:** 0.8.x
- **livekit-plugins-anthropic:** Claude LLM plugin
- **livekit-plugins-deepgram:** Deepgram STT plugin
- **livekit-plugins-silero:** VAD plugin
- **livekit-plugins-cartesia:** Cartesia TTS plugin
- **langchain:** 0.2.x
- **langgraph:** 0.1.x — debate orchestration graph
- **llama-index:** 0.10.x — document ingestion and chunking
- **llama-index-readers-web:** web page fetching
- **chromadb:** 0.5.x — embedded vector store (no server)
- **sentence-transformers:** 2.7.x — local embeddings (all-MiniLM-L6-v2)
- **sqlalchemy:** 2.0.x — ORM
- **pydantic-settings:** 2.x — config management
- **PyInstaller:** 6.x — package Python to exe

---

## Environment Variables

All variables go in `.env` at project root (dev) or stored in OS keychain (production).

```env
# LiveKit (free tier at livekit.io/cloud)
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=your_api_key
LIVEKIT_API_SECRET=your_api_secret

# Anthropic
ANTHROPIC_API_KEY=your_claude_key

# Deepgram (free $200 credit at deepgram.com)
DEEPGRAM_API_KEY=your_deepgram_key

# Cartesia (free tier at cartesia.ai)
CARTESIA_API_KEY=your_cartesia_key

# Sidecar runtime (set by Electron, do not set manually)
FORGE_DATA_DIR=/path/to/user/data
FORGE_PORT=8765
```

---

## Electron Main Process — Critical Behaviors

### Sidecar Management (`electron/main.js`)

```javascript
// Sidecar binary path resolution
const SIDECAR_PATH = app.isPackaged
  ? path.join(process.resourcesPath, 'sidecar', 'forge_chamber.exe')
  : path.join(__dirname, '..', 'sidecar', 'dist', 'forge_chamber.exe')

// Data directory — all local data lives here
const DATA_DIR = path.join(app.getPath('userData'), 'ForgeChamber')

// Startup sequence:
// 1. ensureDataDir()
// 2. loadApiKeysFromKeychain() → set as env vars for sidecar
// 3. startSidecar() — spawn with windowsHide: true
// 4. waitForSidecar() — poll GET /health with 30 retries × 500ms
// 5. loadSplash() → on sidecar ready → loadApp()

// On app-before-quit: kill sidecar process
// On sidecar unexpected exit: restart it, notify renderer via IPC
```

### IPC Handlers (expose via `ipcMain.handle`)

```javascript
// File system
'pick-files'        // → dialog.showOpenDialog (pdf, docx, txt, md)
'read-file'         // → fs.readFileSync(path) → Buffer
'get-data-dir'      // → DATA_DIR string

// API keys (keychain)
'save-api-keys'     // → electron-keytar set all keys
'get-api-keys'      // → electron-keytar get all keys (never expose to renderer raw)
'has-api-keys'      // → boolean — used to decide onboarding vs dashboard

// App updates
'install-update'    // → autoUpdater.quitAndInstall()
```

### Preload (`electron/preload.js`)

```javascript
// Expose ONLY these on window.electronAPI
contextBridge.exposeInMainWorld('electronAPI', {
  pickFiles: () => ipcRenderer.invoke('pick-files'),
  readFile: (path) => ipcRenderer.invoke('read-file', path),
  saveApiKeys: (keys) => ipcRenderer.invoke('save-api-keys', keys),
  hasApiKeys: () => ipcRenderer.invoke('has-api-keys'),
  onUpdateReady: (cb) => ipcRenderer.on('update-ready', cb),
  installUpdate: () => ipcRenderer.invoke('install-update'),
  getSidecarPort: () => 8765,
})
```

---

## FastAPI Sidecar — API Contract

### Base URL
`http://127.0.0.1:8765`

### Endpoints

```
GET  /health
     → { status: "ok", version: "1.0.0" }

POST /engineer/setup
     Body: { name, role_track, skill_level }
     → { id, name, role_track, total_xp: 0 }

GET  /engineer/profile
     → EngineerProfile

POST /rag/ingest-url
     Body: { url: string }
     → { status: "ingested", chunks: number, title: string }

POST /rag/ingest-file
     Body: multipart/form-data { file }
     → { status: "ingested", chunks: number, title: string }

GET  /rag/sources
     → [ { id, label, chunks, ingested_at } ]

DELETE /rag/source/{source_id}
     → { status: "deleted" }

POST /session/start
     Body: { topic, agents: string[], user_role, room_id }
     → { livekit_url, livekit_token, room_name, session_id }

GET  /session/{session_id}
     → SessionDetail (transcript, debrief, scores)

GET  /session/list
     → [ SessionSummary ]

POST /session/{session_id}/end
     Body: { transcript: Turn[] }
     → { debrief, scores, xp_earned }

GET  /progress/skills
     → { technical_depth, communication, debate_resilience, ai_native } (scores 1-5)

GET  /progress/sessions
     → [ { date, topic, xp, scores } ]
```

---

## Agent Personas — Implementation Contract

Store all personas in `sidecar/agents/personas.py` as a Python dict.
Each persona MUST have:

```python
PERSONAS = {
    "sre": {
        "name": "Alex",
        "role": "SRE",
        "voice_id": "694f9389-aac1-45b6-b726-9d9369183238",  # Cartesia voice ID
        "color": "#E8533A",
        "greeting": "SRE here. What are you building — and what breaks first?",
        "system": """...(full persona system prompt)...""",
        "quiz_topics": ["SLO definition", "blast radius", "runbook contents"],
        "disagreement_triggers": ["missing monitoring", "no rollback plan"],
    },
    "sys_arch": { ... },
    "cloud_eng": { ... },
    "java_dev":  { ... },
    "ui_dev":    { ... },
}
```

### System Prompt Template (use for all agents)

```
You are {name}, {role}, in a live engineering debate panel in Forge Chamber.

CONTEXT: You are speaking with other engineers on the panel.
The student engineer is listening and may jump in at any time.
If the student has not spoken for 5+ turns, you MUST address them directly with a question.

YOUR MANDATE: {mandate}

YOUR STYLE: {style_description}

YOUR TRIGGER POINTS — always push back on:
{trigger_list}

DEBATE RULES:
- Keep turns SHORT: 2–4 sentences maximum
- React DIRECTLY to what was just said — no summaries, no repetition
- End EVERY turn with either a question to another agent or to the student
- Address agents by name when challenging them directly
- When addressing the student, be direct but not harsh

CURRENT CONTEXT:
Topic: {topic}
{rag_context_block}

RECENT DEBATE:
{transcript_last_8_turns}
```

---

## Debate Orchestration — LangGraph Graph

```python
# sidecar/agents/orchestrator.py

# Graph nodes:
# 1. route_turn      → decides next speaker + seed (Claude Haiku call)
# 2. generate_turn   → generates utterance for selected agent (Claude Sonnet call)
# 3. detect_quiz     → checks if user has been silent too long (local logic, no LLM)
# 4. wait_for_human  → pauses graph, listens for human speech event
# 5. resume_debate   → resumes after human speaks

# Graph edges:
# route_turn → generate_turn
# generate_turn → detect_quiz
# detect_quiz → [wait_for_human (if quiz) | route_turn (if not)]
# wait_for_human → resume_debate (on human speech event)
# resume_debate → route_turn

# State schema:
class DebateState(TypedDict):
    topic: str
    agents: list[str]
    transcript: list[dict]
    turn_count: int
    active_speaker: str | None
    human_silent_turns: int
    is_paused: bool
    rag_context: str
    session_id: str
```

---

## RAG Pipeline — Implementation Rules

1. **Chunking:** 500 token window, 50 token overlap, using LlamaIndex `SentenceSplitter`
2. **Embedding model:** `all-MiniLM-L6-v2` via sentence-transformers — load ONCE at sidecar startup, reuse
3. **ChromaDB:** PersistentClient at `{DATA_DIR}/chroma` — one collection `forge_context`
4. **Query:** Per agent turn, query with the last 2 utterances concatenated, retrieve top 4 chunks
5. **Injection:** Prepend retrieved chunks to agent system prompt in a clearly delimited block:

```
== REFERENCE MATERIAL ==
The engineer has shared the following context. Ground your debate in this material 
where relevant. Do not quote it directly — reason from it.

[From: confluence-architecture.html]
...chunk text...

[From: uploaded-design-doc.pdf]
...chunk text...
== END REFERENCE MATERIAL ==
```

6. **Source tracking:** Every ingested source logged in `{DATA_DIR}/sources.json`
7. **Cleanup:** On Room end, optionally purge room-specific chunks from ChromaDB

---

## Voice Pipeline — Implementation Rules

1. **STT:** Use `livekit-plugins-deepgram` with `model="nova-2"`, `language="en-US"`, `smart_format=True`
2. **TTS:** Use `livekit-plugins-cartesia` — each agent MUST have a different `voice_id`
3. **VAD:** Use `livekit-plugins-silero` — default sensitivity, `min_silence_duration=0.5`
4. **Interrupt handling:** Built into `VoiceAssistant` — set `allow_interruptions=True` on all `.say()` calls
5. **Agent announcement:** Before each agent speaks, publish a data channel message:

```json
{ "type": "speaker_change", "agent_key": "sre", "agent_name": "Alex", "agent_role": "SRE" }
```

6. **Transcript sync:** After each utterance, publish:

```json
{
  "type": "turn_committed",
  "speaker_type": "agent",
  "speaker_key": "sre",
  "speaker_name": "Alex",
  "text": "...utterance text...",
  "turn_number": 7
}
```

---

## UI Component Specifications

### Color System
```css
:root {
  --brand: #2B5EA7;
  --accent: #E8533A;
  --surface: #F9F8F5;
  --surface-2: #EEECE8;
  --text-primary: #1A1A2E;
  --text-secondary: #555566;
  --text-tertiary: #8888AA;
  --border: rgba(0,0,0,0.12);

  /* Agent colors */
  --agent-sre: #E8533A;
  --agent-arch: #2B5EA7;
  --agent-cloud: #1D9E75;
  --agent-java: #BA7517;
  --agent-ui: #7F77DD;
  --agent-human: #2A7A2A;
}
```

### VoiceBar Component
- Full-width bar at bottom of RoomActive page
- Shows animated waveform (CSS animation, not canvas) when any speaker is active
- Speaker name + role displayed left of waveform
- "Join Debate" button right side — green when Listen Mode, transitions to "Speaking..." when active
- Spacebar toggles join/leave (keyboard shortcut)
- Mic mute button with visual state

### TranscriptFeed Component
- Scrolling list of Turn cards
- Each card: agent color bar on left edge, agent name + role top, text content, timestamp
- Human turns: distinct background, "You" label
- Quiz Events: amber accent, "You were asked:" prefix
- Auto-scrolls to bottom on new turn
- Smooth scroll animation

### SkillRadar Component
- Pure SVG, no external library
- 4 axes: Technical Depth, Communication, Debate Resilience, AI-Native
- Scores plotted as polygon
- Axes labeled at tips
- Animate score polygon changes with CSS transition

### AgentPanel Component  
- Row of agent cards (compact) at top of RoomActive
- Each card: agent name, role, color dot
- Active speaker: animated ring around card, slightly enlarged
- Idle: normal state

---

## Debrief Generation — Synthesis Prompt

After session end, call Claude Sonnet with this system prompt:

```
You are the Forge Chamber session analyst. Analyze this engineering debate transcript 
and produce a structured debrief for the learning engineer.

Respond ONLY with valid JSON, no markdown, no preamble:
{
  "key_insights": ["insight 1", "insight 2", "insight 3"],
  "strong_moments": [
    { "turn": <number>, "speaker": "human", "observation": "..." }
  ],
  "knowledge_gaps": [
    { "topic": "...", "context": "...", "suggested_study": "..." }
  ],
  "scores": {
    "technical_depth": <1-5>,
    "communication": <1-5>,
    "debate_resilience": <1-5>,
    "ai_native": <1-5>
  },
  "overall_comment": "One paragraph honest assessment of this session."
}

Scoring rubric:
1 = Did not engage with this dimension
2 = Attempted but showed significant gaps
3 = Competent — handled most challenges adequately
4 = Strong — clear understanding, well-articulated under pressure
5 = Exceptional — nuanced, accurate, held position with evidence
```

---

## Build Process

### Development Mode

```bash
# Terminal 1: Start Python sidecar in dev mode
cd sidecar
python main.py

# Terminal 2: Start LiveKit agent worker
cd sidecar
python voice/livekit_worker.py dev

# Terminal 3: Start React dev server
cd renderer
npm run dev

# Terminal 4: Start Electron pointing at dev renderer
cd electron
RENDERER_URL=http://localhost:5173 npm run dev
```

### Production Build

```bash
# Step 1: Build Python sidecar → single exe
cd sidecar
pip install -r requirements.txt
pyinstaller forge_chamber.spec
# Output: sidecar/dist/forge_chamber.exe (~180MB)

# Step 2: Build React renderer
cd renderer
npm run build
# Output: renderer/dist/

# Step 3: Package with electron-builder
cd electron
npm run build
# Output: electron/dist/Forge Chamber Setup 1.0.0.exe
```

### PyInstaller Spec Key Settings

```python
# forge_chamber.spec
exe = EXE(
    ...
    name='forge_chamber',
    console=False,      # No terminal window
    onefile=True,       # Single exe
    ...
)
```

---

## Error Handling Standards

- **Sidecar fails to start:** Show error screen with "Restart App" button and log path
- **LLM API error:** Show in transcript as system message; retry once; skip turn if retry fails
- **STT connection lost:** Pause session, show reconnect indicator, auto-retry every 5s
- **Context ingestion fails:** Show error in ContextDrop; allow retry; never crash the Room
- **Session data write fails:** Log error; show warning; continue session in memory

---

## Testing Requirements

For POC phase, implement these minimum tests:

```
sidecar/tests/
├── test_rag.py          # ingest URL, ingest file, retrieve context
├── test_personas.py     # each persona generates valid utterance
├── test_debrief.py      # synthesis produces valid JSON debrief
├── test_db.py           # CRUD operations on all tables
└── test_api.py          # API route happy paths

renderer/src/tests/
├── VoiceBar.test.tsx     # renders in listen/active states
├── TranscriptFeed.test.tsx  # renders turns, auto-scrolls
└── SkillRadar.test.tsx   # SVG renders with score data
```

---

## What NOT to Do

- Do NOT use PostgreSQL, Redis, or Docker for anything — SQLite + embedded ChromaDB only
- Do NOT use heavy chart libraries (Recharts, Chart.js) — SVG only for SkillRadar
- Do NOT store audio recordings — transcript text only
- Do NOT make API calls from the renderer directly — always go through the FastAPI sidecar
- Do NOT hardcode API keys anywhere in code — always use environment variables or keychain
- Do NOT use `process.env` in renderer — only in main process and preload
- Do NOT use `any` TypeScript types — fully type all interfaces
- Do NOT build a web app — this is a desktop Electron app, deploy accordingly
