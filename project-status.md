# Forge Chamber — Project Status

Last updated: 2026-03-24
Active branch: develop

## Overall Progress

| EPIC | Title | Status | Completion |
|------|-------|--------|------------|
| E1 | Foundation & Repository Setup | ✅ Complete | 100% |
| E2 | Electron Shell & App Infrastructure | ✅ Complete | 100% |
| E3 | Python Sidecar & FastAPI Backend | ✅ Complete | 100% |
| E4 | Voice Pipeline Integration | ✅ Complete | 100% |
| E5 | Multi-Agent Debate Engine | ⬜ Not Started | 0% |
| E6 | RAG Pipeline | ⬜ Not Started | 0% |
| E7 | React UI | ⬜ Not Started | 0% |
| E8 | Skills & XP | ⬜ Not Started | 0% |
| E9 | Testing & QA | ⬜ Not Started | 0% |
| E10 | CI/CD & Distribution | ⬜ Not Started | 0% |

## Current Sprint

**Sprint 2 — Weeks 2–4**
Goal: Debate engine, RAG ingestion, React UI

### Next Tasks
- [ ] E5-T1: Agent persona definitions (5 agents with full system prompts)
- [ ] E5-T2: LangGraph debate orchestrator
- [ ] E5-T3: Debate engine with autonomous loop + human interrupt
- [ ] E6-T1: RAG ingestion (LlamaIndex + ChromaDB)

## Completed Sprints

### Sprint 1 — Weeks 1–2 (DONE)
Goal: App launches, sidecar responds to /health

#### E1 — Foundation & Repository Setup
- [x] E1-T1: Directory structure (frontend/, desktop/, mobile/, backend/, scripts/)
- [x] E1-T2: backend/requirements.txt — all packages pinned to exact versions
- [x] E1-T3: frontend/package.json + desktop/package.json with all deps
- [x] E1-T4: All config files (.env.example, .gitignore, bootstrap scripts, .vscode, tsconfig, vite.config, tailwind.config, capacitor.config)

#### E2 — Electron Shell & App Infrastructure
- [x] E2-T1: desktop/main.js — BrowserWindow, sidecar spawn/poll/restart, splash, lifecycle
- [x] E2-T2: desktop/preload.js — contextBridge with 8 invoke channels + 3 event channels
- [x] E2-T3: Electron builder config in package.json (NSIS, extraResources, publish)
- [x] E2-T4: desktop/splash.html — dark branded loading screen with CSS animation
- [x] Placeholder icon assets (icon.ico + icon.png)

#### E3 — Python Sidecar & FastAPI Backend
- [x] E3-T1: backend/main.py — lifespan, CORS localhost-only, JSON exception handler, SIGTERM
- [x] E3-T2: backend/db/ — async SQLAlchemy, 5 ORM tables, PRAGMA foreign_keys, full CRUD
- [x] E3-T3: backend/api/routes/ — all 14 REST endpoints (health, engineer, session, rag, progress)
- [x] E3-T4: backend/core/config.py — pydantic-settings with DB mode + chroma mode for Phase 2

**Verified:** Server starts, GET /health returns `{"status":"ok","version":"1.0.0"}`, all 14 routes registered.

#### E4 — Voice Pipeline Integration
- [x] E4-T1: backend/voice/livekit_worker.py — LiveKit agent worker with Groq LLM (llama-3.3-70b-versatile via livekit-plugins-openai), Deepgram STT (nova-2), Silero VAD, Cartesia TTS
- [x] E4-T2: backend/voice/tts_router.py — VOICE_IDS for all 5 agents, get_tts_for_agent()
- [x] E4-T3: session.py updated — _dispatch_agent_to_room() creates LiveKit room + dispatches agent worker
- [x] E4-T4: requirements.txt updated — all LiveKit plugins at 1.5.0, livekit-plugins-openai added, GROQ_API_KEY in config

**Verified:** Worker registers with LiveKit Cloud (Singapore South East region), POST /session/start returns valid JWT token, worker receives job request within 2 seconds, Cartesia TTS WebSocket + Deepgram STT WebSocket both established.

## Decisions Log

| Date | Decision | Reason |
|------|----------|--------|
| 2025-01-23 | SSH key setup for WSL | Eliminate PAT prompts on git push |
| 2025-01-23 | LiveKit Cloud free tier | No local Docker/WebRTC server needed |
| 2025-01-23 | SQLite over PostgreSQL | Zero setup for end users |
| 2026-03-24 | Multi-platform architecture (Option C) | One React codebase, three wrappers (Electron, web, Capacitor) |
| 2026-03-24 | Renamed sidecar/ to backend/, renderer/ to frontend/, electron/ to desktop/ | Clearer naming for multi-platform |
| 2026-03-24 | usePlatform() hook as key abstraction | Components never call Electron/Capacitor directly |
| 2026-03-24 | RAG routes stubbed in E3, full impl deferred to E6 | Get API shape right early, real ingestion later |
| 2026-03-24 | LiveKit token generation with graceful fallback | Allows backend to start without LiveKit keys configured |
| 2026-03-24 | Groq replaces Anthropic for all LLM calls | Faster inference, OpenAI-compatible API via livekit-plugins-openai |
| 2026-03-24 | LiveKit plugins upgraded from 1.0.14 to 1.5.0 | Required for livekit-agents 1.5.0 API compatibility (Agent+AgentSession pattern) |

## Blockers
_none_

## Notes
- Dev machine: HP Pavilion 15-eg2xxx, i7-1255U, 16GB RAM, Windows 11 Pro
- WSL2 Ubuntu for development
- Claude Code Max for implementation
- Python 3.11 venv at backend/.venv
- LiveKit agents 1.5.0 uses Agent + AgentSession pattern (not VoiceAssistant)
- Groq model: llama-3.3-70b-versatile (agent utterances), llama-3.1-8b-instant (orchestrator routing)
- Worker registered at: wss://forge-chamber-osr8q0w6.livekit.cloud

## How to use it with Claude Code

Update it manually after each session. When you start a new Claude Code session after a gap, add this to your opening prompt:
```
Read CLAUDE.md, Forge-Chamber-Dev-Guide.md, and project-status.md.
project-status.md shows where we are. Continue from the next incomplete task.
```
