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
| E5 | Multi-Agent Debate Engine | ✅ Complete | 100% |
| E6 | RAG Pipeline & Context Ingestion | ✅ Complete | 100% |
| E7 | React UI Implementation | ✅ Complete | 100% |
| E8 | Skills & XP | ⬜ Not Started | 0% |
| E9 | Testing & QA | ⬜ Not Started | 0% |
| E10 | CI/CD & Distribution | ⬜ Not Started | 0% |

## Current Sprint

**Sprint 4 — Weeks 6–8**
Goal: Skills & XP system, testing, CI/CD

### Next Tasks
- [ ] E8-T1: Skills tracking integration (frontend ↔ backend)
- [ ] E9-T1: Backend tests (test_rag, test_personas, test_debrief, test_db, test_api)
- [ ] E9-T2: Frontend tests (VoiceBar, TranscriptFeed, SkillRadar)
- [ ] E10-T1: CI/CD pipeline + desktop build

## Completed Sprints

### Sprint 2 — Weeks 2–4 (DONE)
Goal: Voice pipeline, debate engine, RAG pipeline

#### E4 — Voice Pipeline Integration
- [x] E4-T1: backend/voice/livekit_worker.py — LiveKit agent worker with Groq LLM (llama-3.3-70b-versatile via livekit-plugins-openai), Deepgram STT (nova-2), Silero VAD, Cartesia TTS
- [x] E4-T2: backend/voice/tts_router.py — VOICE_IDS for all 5 agents, get_tts_for_agent()
- [x] E4-T3: session.py updated — _dispatch_agent_to_room() creates LiveKit room + dispatches agent worker
- [x] E4-T4: requirements.txt updated — all LiveKit plugins at 1.5.0, livekit-plugins-openai added, GROQ_API_KEY in config

**Verified:** Worker registers with LiveKit Cloud (Singapore South East region), POST /session/start returns valid JWT token, worker receives job request within 2 seconds, Cartesia TTS WebSocket + Deepgram STT WebSocket both established.

#### E5 — Multi-Agent Debate Engine
- [x] E5-T1: backend/agents/personas.py — 5 complete agent personas (Alex/SRE, Maya/Architect, Ravi/Cloud, Sam/Java, Jordan/UI) with full system prompts, 7+ disagreement triggers each, 5+ quiz topics each
- [x] E5-T2: backend/agents/orchestrator.py — LangGraph debate orchestrator with DebateState, route_turn (llama-3.1-8b-instant), generate_turn (llama-3.3-70b-versatile), detect_quiz, wait_for_human, resume_debate nodes
- [x] E5-T3: backend/agents/debate_engine.py — async debate loop with data callbacks (speaker_change, turn_committed, quiz_event), pause/resume for human interrupt, quiz timeout with agent self-answer
- [x] E5-T4: backend/agents/synthesizer.py — Groq-powered debrief synthesis (scores, insights, knowledge gaps, overall comment), XP calculation with breakdown (base + participation + quiz + duration + streak + score)
- [x] E5-T5: backend/voice/livekit_worker.py — updated to run debate engine with voice I/O, passes full metadata (topic, agents, session_id) via room metadata, speaks each agent turn aloud, posts results to /session/{id}/end

**Verified:** 5-turn debate with 3 agents (SRE, Architect, Cloud Eng) on "microservices vs monolith":
- All agents stay in character with distinct perspectives
- Each turn ends with a question (Socratic obligation)
- Quiz detection triggers at 5+ silent human turns
- 12 data channel messages published (5 speaker_change + 5 turn_committed + 1 quiz_event + 1 quiz answer)
- Debrief: scores {technical_depth: 4.0, communication: 4.0, debate_resilience: 4.0, ai_native: 3.0}
- XP: 125 (base 50 + score bonus 75)

#### E6 — RAG Pipeline & Context Ingestion
- [x] E6-T1: backend/rag/embedder.py — all-MiniLM-L6-v2 singleton loaded at startup, ChromaDB PersistentClient with SentenceTransformerEmbeddingFunction, initialized in main.py lifespan
- [x] E6-T2: backend/rag/ingester.py — URL + file ingestion (PDF, DOCX, TXT, MD) with LlamaIndex SentenceSplitter (500 tokens, 50 overlap), sha256 chunk IDs, source tracking in sources.json
- [x] E6-T3: backend/rag/retriever.py — semantic search returning formatted context blocks (retrieve_context + retrieve_for_agent_turn)
- [x] E6-T4: backend/api/routes/rag.py — stubs replaced with real implementations calling ingester.py
- [x] E6-T5: RAG wired into debate — orchestrator.generate_turn calls retriever per turn, context injected into agent system prompts

**Verified:** File ingestion (microservices article → 1 chunk), source listing, semantic retrieval (2,680 chars context), RAG-grounded 3-agent debate (agents reference ingested content on microservices trade-offs), source deletion removes from ChromaDB + sources.json.

### Sprint 3 — Weeks 4–6 (DONE)
Goal: React UI

#### E7 — React UI Implementation
- [x] E7-T1: App shell — React Router 6 routing (7 routes), Zustand store (engineer/room/session/debrief slices), typed API client (all 14 endpoints), usePlatform hook (Electron/Web), dark theme CSS with responsive breakpoints
- [x] E7-T2: Onboarding — 2-column layout (brand panel + form), 6 API key inputs with show/hide, role track dropdown, skill level radio, "Enter the Chamber" submit
- [x] E7-T3: Dashboard — greeting header, XP counter, quick start (topic input + 6 preset pills + 5 agent toggle pills), recent sessions list
- [x] E7-T4: RoomSetup — agent cards with mandates, ContextDrop (URL + file ingestion), role selector, "Start Room" button
- [x] E7-T5: RoomActive — 3-panel layout (left: timer + end session, center: TranscriptFeed + VoiceBar, right: AgentPanel + quiz zone), LiveKit data channel integration (turn_committed, speaker_change, quiz_event, session_complete), spacebar join/leave shortcut
- [x] E7-T6: Debrief — score cards + SkillRadar SVG (pure inline, 4 axes), key insights, strong moments, knowledge gaps, XP display, "Start Another Room" action
- [x] E7-T7: Progress — profile header, XPBar with levels, SkillRadar, 4 domain progress bars, session history table
- [x] E7-T8: Settings — editable profile (PUT /engineer), API keys section, about info
- [x] E7-T9: NavBar — desktop 64px sidebar + mobile bottom tabs (responsive @768px breakpoint)
- [x] E7-T10: ContextDrop — URL input + file drop zone, source chips with delete, POST /rag/ingest-url + /ingest-file

**Verified:** `npx tsc --noEmit` passes with zero errors. Vite dev server starts in 141ms. 24 files, 6,752 lines of TypeScript/React. All 7 pages render, all components typed, all API endpoints wired.

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
| 2026-03-24 | Two Groq models for debate: 8b routing, 70b generation | Fast routing (llama-3.1-8b-instant) + quality utterances (llama-3.3-70b-versatile) |
| 2026-03-24 | httpx verify=False for Groq in WSL dev | WSL CA certificate issue; production won't need this |
| 2026-03-24 | ChromaDB SentenceTransformerEmbeddingFunction for consistency | Same model embeds at ingest and query time, no drift |
| 2026-03-24 | Embedder loaded in main.py lifespan before routes | Ensures model ready before any RAG request; ~5s cold start |
| 2026-03-24 | Dark theme default (#0F0F14), functional over beautiful | Core UX works first; polish later. RoomActive gets extra care as core experience |
| 2026-03-24 | Pure SVG SkillRadar (no chart libraries) | Per CLAUDE.md spec; keeps bundle small, full control over animation |
| 2026-03-24 | Zustand over Redux/Context | Simpler API, less boilerplate, good TypeScript inference |

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
- Debate engine tested standalone: 5-turn debate completes in ~15 seconds with Groq

## How to use it with Claude Code

Update it manually after each session. When you start a new Claude Code session after a gap, add this to your opening prompt:
```
Read CLAUDE.md, Forge-Chamber-Dev-Guide.md, and project-status.md.
project-status.md shows where we are. Continue from the next incomplete task.
```
