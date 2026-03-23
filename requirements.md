# Forge Chamber — Functional Requirements, Flows & Design

**Version:** 1.0  
**Product:** Forge Chamber Desktop App  
**Program:** Ascendion Forge Engineering Elevation  
**Author:** Solutions Architecture, Ascendion Digital Services  
**Status:** Draft — POC Phase

---

## Table of Contents

1. [Product Vision](#1-product-vision)
2. [User Personas](#2-user-personas)
3. [Core Concepts & Terminology](#3-core-concepts--terminology)
4. [Functional Requirements](#4-functional-requirements)
5. [User Flows](#5-user-flows)
6. [Agent Persona Specifications](#6-agent-persona-specifications)
7. [Learning & Skill Framework](#7-learning--skill-framework)
8. [Data Model](#8-data-model)
9. [Non-Functional Requirements](#9-non-functional-requirements)
10. [Out of Scope for POC](#10-out-of-scope-for-poc)

---

## 1. Product Vision

Forge Chamber is a standalone desktop application that creates a voice-first, adversarial learning environment for software engineers. Users enter a "Room" where multiple AI agents — each with a distinct engineering role, opinion, and communication style — debate a technical topic. The user listens, participates, gets quizzed, and builds the ability to articulate, defend, and reason through technical decisions under pressure.

### 1.1 Design Principles

- **Voice-first, not voice-only.** Voice is the primary interaction mode. Text is available as a parallel channel, never the primary one.
- **Adversarial by design.** Agents disagree with each other. Agreement is the exception, not the default.
- **The user is never a passive observer for long.** Agents will call on the user directly within 3–5 turns if they have not participated.
- **Context is king.** Every debate is grounded — either in the user's own documents, a URL, or a specific topic they have defined.
- **Zero setup for the end user.** Engineers download one installer. No Python, no Docker, no configuration.
- **Persistent, private, local.** All session data lives on the user's machine. Nothing is sent to external servers except LLM API calls and voice streaming.

---

## 2. User Personas

### 2.1 Primary: The Learner Engineer
- Mid-level software engineer (2–6 years experience) at Ascendion
- Assigned to a client engagement, needs to rapidly build competency in an area
- Comfortable with technology but not with defending technical decisions verbally
- Motivation: promotion, better client performance, confidence in technical discussions

### 2.2 Secondary: The Senior Practitioner
- Senior engineer or Solutions Architect using Chamber to pressure-test their own thinking
- Uses Review Mode with their own architecture docs or design proposals
- Motivation: pre-flight check before a client presentation, rubber-duck at senior level

### 2.3 Tertiary: The Mentor / Manager
- Engineering manager using Chamber to assign specific learning scenarios to their team
- Views aggregated skill progress across their reports (future phase)
- Motivation: visible evidence of team skill development

---

## 3. Core Concepts & Terminology

| Term | Definition |
|------|-----------|
| **Room** | A single debate session. Has a topic, a set of agents, a user role, and a context. |
| **Agent** | An AI persona with a defined role, mandate, communication style, and disagreement triggers. |
| **Context** | The reference material that grounds the debate: URLs, documents, voice notes, or a plain topic. |
| **User Role** | The engineering role the user assumes in the Room (e.g., "Junior Java Developer"). |
| **Turn** | A single utterance by one agent or the user. |
| **Quiz Event** | A moment when an agent directly addresses the user with a question that requires a response. |
| **Socratic Obligation** | The requirement that every agent turn ends with a question, either to another agent or to the user. |
| **Session** | A completed Room interaction. Stored with full transcript, skill assessment, and XP. |
| **XP** | Experience Points earned per session, accumulated across the engineer's profile. |

---

## 4. Functional Requirements

### 4.1 Application Shell

| ID | Requirement | Priority |
|----|-------------|----------|
| SH-01 | App installs via a single `.exe` (Windows) or `.dmg` (macOS) with no prerequisites | P0 |
| SH-02 | App auto-starts a bundled Python sidecar on launch, hidden from the user | P0 |
| SH-03 | First-launch onboarding screen collects engineer name, role, and API keys | P0 |
| SH-04 | App checks for updates silently on startup and notifies user when available | P1 |
| SH-05 | All local data stored in platform user data directory with no cloud sync | P0 |
| SH-06 | App works fully offline except for LLM API calls and voice streaming | P0 |

### 4.2 Room Creation

| ID | Requirement | Priority |
|----|-------------|----------|
| RM-01 | User can create a new Room with a name and a topic | P0 |
| RM-02 | Topic can be entered as free text (up to 500 chars) | P0 |
| RM-03 | Topic can be selected from a curated library of 20+ engineering scenarios | P1 |
| RM-04 | User selects 2–4 AI agents to participate in the Room | P0 |
| RM-05 | User selects their own role in the Room (from a predefined list matching their skill level) | P0 |
| RM-06 | Room creation validates that at least 2 agents are selected before starting | P0 |
| RM-07 | User can save Room configuration as a template for reuse | P2 |

### 4.3 Context Ingestion

| ID | Requirement | Priority |
|----|-------------|----------|
| CTX-01 | User can add context by pasting one or more URLs (web pages, Confluence, GitHub) | P0 |
| CTX-02 | User can upload PDF, DOCX, TXT, or Markdown files as context | P0 |
| CTX-03 | User can record a voice note as context (up to 2 minutes) | P1 |
| CTX-04 | Voice note is transcribed and stored as text context | P1 |
| CTX-05 | Context is chunked, embedded, and stored in a local vector store | P0 |
| CTX-06 | UI shows list of ingested sources with chunk count and status | P0 |
| CTX-07 | User can remove a context source before or during a Room session | P1 |
| CTX-08 | Agents are informed at Room start that context has been provided | P0 |
| CTX-09 | RAG retrieval runs per agent turn using the current transcript as the query | P0 |

### 4.4 Voice Pipeline

| ID | Requirement | Priority |
|----|-------------|----------|
| VP-01 | User microphone captured via browser-standard Web Audio API in Electron | P0 |
| VP-02 | Voice Activity Detection (VAD) identifies when user starts and stops speaking | P0 |
| VP-03 | Speech-to-text converts user utterance to text in real-time with < 500ms latency | P0 |
| VP-04 | Text-to-speech synthesizes each agent response with a distinct voice per agent | P0 |
| VP-05 | TTS audio streams — playback begins before synthesis is complete | P0 |
| VP-06 | User speech interrupts agent TTS playback immediately | P0 |
| VP-07 | Visual waveform indicator shows who is currently speaking (agent name or "You") | P0 |
| VP-08 | User can mute/unmute microphone without ending the session | P0 |
| VP-09 | User can adjust speaker volume independently from mic sensitivity | P1 |
| VP-10 | Full session audio is not recorded or stored — only transcript text is persisted | P0 |

### 4.5 Multi-Agent Debate Engine

| ID | Requirement | Priority |
|----|-------------|----------|
| AG-01 | Agents take turns autonomously based on orchestrator logic | P0 |
| AG-02 | Each agent turn is seeded by the orchestrator with a topic cue | P0 |
| AG-03 | Orchestrator uses Claude Haiku for turn-routing (cheap, fast) | P0 |
| AG-04 | Each agent uses Claude Sonnet for utterance generation (quality) | P0 |
| AG-05 | Agent turns are 2–4 sentences by default (configurable per persona) | P0 |
| AG-06 | Agent can directly address another agent by name to challenge them | P0 |
| AG-07 | Challenged agent is prioritized as next speaker by the orchestrator | P0 |
| AG-08 | Agents rotate through all participants — no agent skipped for more than 3 turns | P0 |
| AG-09 | Orchestrator increases tension after 3+ agreeable turns | P1 |
| AG-10 | Every agent turn ends with either a question to another agent or to the user | P0 |
| AG-11 | Shared transcript (text) is passed to each agent as context — agents do not process each other's audio | P0 |

### 4.6 User Participation

| ID | Requirement | Priority |
|----|-------------|----------|
| UP-01 | User starts in Listen Mode by default — mic disabled, agents debate autonomously | P0 |
| UP-02 | User can enter Debate Mode at any time by clicking "Join" or pressing spacebar | P0 |
| UP-03 | When user enters Debate Mode, agents pause and yield the floor | P0 |
| UP-04 | After user finishes speaking, agents acknowledge and resume debate | P0 |
| UP-05 | If user has not spoken for 5+ agent turns, an agent addresses them directly (Quiz Event) | P0 |
| UP-06 | Quiz Event asks the user a specific question based on the current debate context | P0 |
| UP-07 | If user does not respond to a Quiz Event within 30 seconds, the asking agent answers the question themselves with a detailed explanation | P0 |
| UP-08 | After answering an unanswered Quiz Event, the agent notes "I'll come back to this" | P1 |
| UP-09 | Agent returns to the same topic/question within the next 3 turns to re-quiz the user | P1 |
| UP-10 | User can explicitly pass on a question ("skip" voice command or button) | P1 |

### 4.7 Session Management

| ID | Requirement | Priority |
|----|-------------|----------|
| SM-01 | Session transcript shown in real-time as scrolling text panel | P0 |
| SM-02 | Each transcript turn labeled with agent name, role, and timestamp | P0 |
| SM-03 | User turns labeled as "You (Engineer)" in the transcript | P0 |
| SM-04 | User can end session at any time | P0 |
| SM-05 | On session end, synthesis agent generates a structured debrief | P0 |
| SM-06 | Debrief includes: key insights from debate, moments the user reasoned well, gaps identified | P0 |
| SM-07 | Debrief is displayed as text and optionally read aloud | P0 |
| SM-08 | Session is persisted to local SQLite with full transcript and debrief | P0 |
| SM-09 | User can replay past session transcripts (text only, no audio) | P1 |
| SM-10 | User can export session transcript as Markdown or PDF | P2 |

### 4.8 Skills & Progress Tracking

| ID | Requirement | Priority |
|----|-------------|----------|
| SK-01 | Each session generates a skill assessment across 4 domains | P0 |
| SK-02 | Skill domains: Technical Depth, Communication Clarity, Debate Resilience, AI-Native Fluency | P0 |
| SK-03 | Assessment scored 1–5 per domain, based on LLM evaluation of transcript | P0 |
| SK-04 | Skill scores accumulated across sessions using weighted rolling average | P1 |
| SK-05 | XP awarded per session based on complexity, duration, and participation level | P0 |
| SK-06 | Progress dashboard shows radar chart of skill profile | P1 |
| SK-07 | Badges awarded for milestones (first debate, defended against SRE, 10 sessions) | P2 |
| SK-08 | Engineer profile page shows total XP, sessions, role track, and skill radar | P1 |

---

## 5. User Flows

### 5.1 First Launch Flow

```
Install app
    │
    ▼
Splash screen (4s — sidecar initializing)
    │
    ▼
Onboarding screen
  ├─ Enter name
  ├─ Select role track (UI Dev / Java Dev / Cloud Eng / SA / SRE)
  ├─ Enter API keys (ANTHROPIC, DEEPGRAM, CARTESIA, LIVEKIT)
  └─ Save → Main Dashboard
```

### 5.2 Create Room Flow

```
Dashboard → "New Room"
    │
    ▼
Room Setup screen
  ├─ Enter topic (free text or pick from library)
  ├─ Select agents (checkboxes: SRE, SA, Cloud, Java, UI Dev)
  ├─ Select your role ("I am a Junior Java Developer")
  └─ Add Context (optional)
        ├─ Paste URL → ingest → show chunk count
        ├─ Upload file → ingest → show chunk count
        └─ Record voice note → transcribe → confirm
    │
    ▼
"Start Room" button
    │
    ▼
Room loads → agents intro themselves → debate begins
```

### 5.3 Active Room Flow

```
Room active — Listen Mode
    │
    ├─ Agent A speaks (TTS plays, transcript updates)
    │       │
    │       └─ Agent B responds (orchestrator picks B, seeds utterance)
    │               │
    │               └─ Agent C challenges A by name (orchestrator prioritizes A next)
    │
    ├─ [After 5 agent turns without user speech]
    │       │
    │       └─ Quiz Event: Agent asks user a direct question
    │               ├─ User responds within 30s → agents acknowledge, continue
    │               └─ User silent → agent answers question, flags "I'll return to this"
    │
    ├─ User clicks "Join Debate" (or presses SPACE)
    │       │
    │       └─ Agents pause → "You" indicator activates → user speaks
    │               │
    │               └─ VAD detects end of speech → agents acknowledge → resume
    │
    └─ User clicks "End Session"
            │
            └─ Debrief generated → displayed → session saved
```

### 5.4 Context Ingestion Flow (during Room Setup)

```
User pastes URL or drops file
    │
    ▼
Frontend sends to FastAPI /rag/ingest-url or /rag/ingest-file
    │
    ▼
LlamaIndex fetches/reads content
    │
    ▼
Text chunked (500 tokens, 50 overlap)
    │
    ▼
sentence-transformers embeds chunks (local, CPU)
    │
    ▼
ChromaDB stores chunks with source metadata
    │
    ▼
UI shows: "confluence-page.html — 47 chunks ingested ✓"
    │
    ▼
On each agent turn: ChromaDB queried with last 2 utterances as query
    │
    ▼
Top 3 chunks injected into agent system prompt as [REFERENCE MATERIAL]
```

### 5.5 Debrief & Skill Assessment Flow

```
User ends session
    │
    ▼
Synthesis Claude call (Sonnet) with full transcript
    │
    ├─ Generates: key debate insights (3 bullets)
    ├─ Generates: moments user reasoned well (2–3 specific references)
    ├─ Generates: knowledge gaps identified (2–3 specific references)
    └─ Scores: Technical Depth, Communication, Debate Resilience, AI-Native (1–5 each)
    │
    ▼
Debrief displayed in UI (text) + read aloud (optional TTS)
    │
    ▼
Session saved to SQLite: transcript, debrief, scores, XP
    │
    ▼
XP animation on dashboard → updated skill radar
```

---

## 6. Agent Persona Specifications

### 6.1 SRE — Alex

- **Voice:** Deep, measured male (Cartesia: sonic-english or custom voice)
- **Mandate:** Production reliability, observability, SLOs, blast radius, incident response, runbooks
- **Communication style:** Direct, slightly combative, always concrete. Cites real incident patterns. Never accepts "we'll fix it later."
- **Disagreement triggers:** Vague SLOs, missing circuit breakers, no monitoring strategy, untested rollback, undefined blast radius, logging gaps
- **Socratic pattern:** Ends every turn with a failure-mode question. "What breaks first?" "Who gets paged?" "What does the runbook say?"
- **Quiz topics:** SLO definition, mean time to recovery, runbook contents, circuit breaker patterns, deployment strategy

### 6.2 Solutions Architect — Maya

- **Voice:** Warm, thoughtful female (Cartesia: distinct voice from SRE)
- **Mandate:** System design, scalability, long-term architecture evolution, trade-off reasoning
- **Communication style:** Socratic by default. Never gives direct answers. Asks what happens at 10x scale, at 18 months, with a team 3x larger.
- **Disagreement triggers:** Short-term thinking, premature optimization, over-engineering, missing bounded contexts, undefined integration contracts
- **Socratic pattern:** Always surfaces the competing concern. "Alex is right about the SLO, but what does that imply for your data model?" 
- **Quiz topics:** CAP theorem application, domain decomposition, API contract design, data consistency models

### 6.3 Cloud / Infrastructure Engineer — Ravi

- **Voice:** Neutral, efficient male
- **Mandate:** AWS/cloud architecture, IaC, networking, egress costs, operational reality, security posture
- **Communication style:** Blunt about cost and ops reality. Catches assumptions that don't survive contact with real cloud constraints.
- **Disagreement triggers:** Hand-wavy cloud assumptions, missing IAM design, no VPC architecture, Lambda misuse, unknown egress costs
- **Socratic pattern:** Ends with an ops or cost question. "Who sets up the IAM roles?" "Have you priced the data transfer?"
- **Quiz topics:** VPC design, IAM least privilege, Lambda cold starts, S3 event architecture, CloudFormation vs Terraform

### 6.4 Senior Java Developer — Sam

- **Voice:** Crisp, methodical male
- **Mandate:** Type safety, JVM performance, transactional integrity, Spring Boot, API design, testing strategy
- **Communication style:** Builds arguments methodically. Cites the Java Memory Model when necessary. Never accepts "it works on my machine."
- **Disagreement triggers:** Unsafe concurrency, missing transaction boundaries, runtime flexibility over compile-time safety, untested edge cases
- **Socratic pattern:** Ends with a correctness or consistency question. "What's the transaction boundary here?" "What happens to the entity if the second operation fails?"
- **Quiz topics:** ACID properties, optimistic vs pessimistic locking, Spring transaction propagation, JVM garbage collection impact, REST vs gRPC

### 6.5 Senior UI Developer — Jordan

- **Voice:** Fast, energetic, slightly informal
- **Mandate:** Component architecture, state management, bundle size, render performance, accessibility, API contracts
- **Communication style:** Practical and fast. Speaks in concrete patterns. Challenges deeply coupled designs and vague API contracts.
- **Disagreement triggers:** Prop drilling, over-fetching APIs, missing loading/error states, inaccessible components, non-normalized state
- **Socratic pattern:** Ends with a user-facing impact question. "How does this load state feel to the user?" "What's the component responsible for owning this data?"
- **Quiz topics:** React render optimization, state normalization, accessibility WCAG compliance, web vitals, micro-frontend trade-offs

---

## 7. Learning & Skill Framework

### 7.1 Skill Domains

| Domain | Definition | Observable Signals |
|--------|-----------|-------------------|
| **Technical Depth** | Accuracy and nuance of technical knowledge demonstrated | Correct use of terminology, accurate trade-off reasoning, absence of misconceptions |
| **Communication Clarity** | Ability to explain complex ideas concisely and precisely | Clear sentence structure under pressure, avoidance of filler phrases, structured arguments |
| **Debate Resilience** | Ability to defend a position under challenge without collapsing or becoming vague | Maintains position with evidence, gracefully revises when shown a better argument |
| **AI-Native Fluency** | Comfort with AI tools, prompting, evaluation, and AI system design concepts | References AI capabilities accurately, understands AI system design patterns |

### 7.2 Role Tracks

| Track | Primary Agents | Key Skill Focus |
|-------|---------------|-----------------|
| UI Developer | Jordan, Maya | React architecture, state, performance, accessibility |
| Java Developer | Sam, Maya | JVM, transactions, API design, testing |
| Cloud Engineer | Ravi, Alex | AWS, IaC, security, cost optimization |
| Solutions Architect | Maya, all | System design, trade-offs, stakeholder communication |
| SRE | Alex, Ravi | Reliability, observability, incident response |

### 7.3 XP Calculation

```
Base XP per session:           50 XP
Complexity multiplier:         1.0–2.0x (based on topic complexity score)
Participation bonus:           +10 XP per debate turn contributed
Quiz answered correctly:       +15 XP
Quiz answered partially:       +5 XP
Full session (>15 min):        +20 XP bonus
Streak bonus (daily sessions): +10 XP per consecutive day
```

### 7.4 Session Scenario Library (Initial 20)

1. Design a high-availability web application on AWS for 1M daily users
2. Build a security layer for a React Native mobile banking app
3. Migrate a monolith to microservices without downtime
4. Design a real-time notification system for 500K concurrent users
5. Build a CI/CD pipeline for a regulated financial services client
6. Choose between REST and GraphQL for a mobile-first API
7. Design a data pipeline for near-real-time fraud detection
8. Build an observability stack for a distributed microservices system
9. Design the caching strategy for a high-read e-commerce platform
10. Handle distributed transactions without a saga framework
11. Kubernetes vs ECS: choosing the right container orchestration
12. Serverless vs containerized workloads for event-driven processing
13. Design a multi-tenant SaaS database architecture
14. Implement RBAC for a complex enterprise application
15. Build a zero-downtime database migration strategy
16. Design an API gateway for a 50-microservice ecosystem
17. Choose a frontend state management approach for a large team
18. Build a resilient event-driven architecture on AWS SQS/SNS
19. Design a logging and alerting strategy for a 24/7 production system
20. Architect a data lake vs data warehouse decision for a fintech client

---

## 8. Data Model

### 8.1 SQLite Tables

```sql
-- Engineers
CREATE TABLE engineers (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    role_track TEXT NOT NULL,
    skill_level TEXT DEFAULT 'mid',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    total_xp INTEGER DEFAULT 0,
    total_sessions INTEGER DEFAULT 0
);

-- Skill progress (rolling averages per domain)
CREATE TABLE skill_scores (
    id TEXT PRIMARY KEY,
    engineer_id TEXT REFERENCES engineers(id),
    domain TEXT NOT NULL,          -- technical_depth | communication | debate_resilience | ai_native
    score REAL NOT NULL,           -- 1.0–5.0
    session_count INTEGER DEFAULT 1,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Rooms (session configurations)
CREATE TABLE rooms (
    id TEXT PRIMARY KEY,
    engineer_id TEXT REFERENCES engineers(id),
    topic TEXT NOT NULL,
    agents TEXT NOT NULL,          -- JSON array of agent keys
    user_role TEXT NOT NULL,
    mode TEXT DEFAULT 'debate',    -- listen | debate | review
    context_sources TEXT,          -- JSON array of source descriptors
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Sessions (completed Room interactions)
CREATE TABLE sessions (
    id TEXT PRIMARY KEY,
    room_id TEXT REFERENCES rooms(id),
    engineer_id TEXT REFERENCES engineers(id),
    started_at DATETIME NOT NULL,
    ended_at DATETIME,
    duration_seconds INTEGER,
    xp_earned INTEGER DEFAULT 0,
    transcript TEXT,               -- JSON array of turns
    debrief TEXT,                  -- JSON: insights, gaps, scores
    technical_depth_score REAL,
    communication_score REAL,
    debate_resilience_score REAL,
    ai_native_score REAL
);

-- Individual debate turns
CREATE TABLE turns (
    id TEXT PRIMARY KEY,
    session_id TEXT REFERENCES sessions(id),
    speaker_type TEXT NOT NULL,    -- agent | human | orchestrator
    speaker_key TEXT,              -- sre | sys_arch | cloud_eng | java_dev | ui_dev | human
    speaker_name TEXT,
    text TEXT NOT NULL,
    is_quiz_event BOOLEAN DEFAULT FALSE,
    quiz_answered BOOLEAN,
    turn_number INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### 8.2 ChromaDB Collections

```
Collection: forge_context
  - Stores chunked context from user-ingested documents and URLs
  - Metadata: { source, source_type, chunk_index, room_id, ingested_at }
  - Queried per agent turn using last 2 utterances as query

Collection: forge_memory  
  - Stores session-level semantic memory per engineer
  - Metadata: { session_id, engineer_id, skill_domain, turn_number }
  - Queried at Room start to surface relevant past session context
```

---

## 9. Non-Functional Requirements

| Category | Requirement |
|----------|-------------|
| **Latency** | End-of-speech to first agent audio byte: < 3.5 seconds (P95) |
| **Latency** | TTS first audio byte after synthesis starts: < 300ms (streaming) |
| **Availability** | App functional without internet for all local operations; voice requires connectivity |
| **Privacy** | No user data, transcripts, or session content transmitted beyond LLM/voice API calls |
| **Security** | API keys stored in OS keychain (electron-keytar), never in plaintext config |
| **Performance** | App usable with 16GB RAM, 4-core CPU; Python sidecar < 500MB RSS |
| **Compatibility** | Windows 10/11 x64 (primary); macOS 12+ (secondary, Phase 2) |
| **Storage** | Local data dir < 2GB for 100 sessions including vector embeddings |
| **Reliability** | Sidecar crash triggers automatic restart with session state preserved |
| **Accessibility** | All controls keyboard-navigable; transcript always readable in parallel with audio |

---

## 10. Out of Scope for POC

The following are explicitly deferred to post-POC phases:

- Manager/admin dashboard and team-level skill reporting
- Real-time multiplayer (multiple human participants in one Room)
- Mobile application
- Custom agent creation by end users
- Integration with Ascendion HRIS or LMS platforms
- AI-generated session video summaries
- macOS distribution (Windows-first for POC)
- Code editor integration (VS Code extension)
- Offline LLM fallback (local model support)
