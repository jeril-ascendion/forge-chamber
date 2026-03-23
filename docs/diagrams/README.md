# Forge Chamber — Architecture Diagrams

16 Mermaid diagrams documenting the Forge Chamber system architecture, user flows, and technical implementation.

## How to Render

- **GitHub**: `.mmd` files render automatically in PRs and file views
- **VS Code**: Install the "Mermaid Preview" extension, then open any `.mmd` file
- **Web**: Copy contents to [mermaid.live](https://mermaid.live) for interactive editing
- **CLI**: `npx @mermaid-js/mermaid-cli mmdc -i file.mmd -o file.svg`

## Diagram Index

### Functional Flows (audience: product, engineering, stakeholders)

| # | File | Purpose |
|---|------|---------|
| 01 | `functional/01-user-journey.mmd` | End-to-end user flow from first launch to skill progression |
| 02 | `functional/02-room-creation.mmd` | Steps from topic selection to starting a live debate room |
| 03 | `functional/03-debate-session.mmd` | What happens during a live multi-agent debate session |
| 04 | `functional/04-context-ingestion.mmd` | How URLs and files become RAG context for agents |
| 05 | `functional/05-debrief-skills.mmd` | How session results turn into skill scores and XP |

### Technical Architecture (audience: engineers, architects)

| # | File | Purpose |
|---|------|---------|
| 06 | `technical/06-system-overview.mmd` | High-level system architecture — all components and services |
| 07 | `technical/07-multi-platform.mmd` | One React codebase serving desktop, web, and mobile |
| 08 | `technical/08-voice-pipeline.mmd` | Audio flow: microphone -> STT -> LLM -> TTS -> speaker |
| 09 | `technical/09-debate-engine.mmd` | LangGraph state machine for multi-agent debate orchestration |
| 10 | `technical/10-rag-pipeline.mmd` | Document ingestion, embedding, storage, and retrieval |
| 11 | `technical/11-database-erd.mmd` | SQLite schema — 5 tables with relationships |

### Sequence Diagrams (audience: engineers implementing features)

| # | File | Purpose |
|---|------|---------|
| 12 | `sequence/12-voice-session.mmd` | Full session lifecycle from start to debrief |
| 13 | `sequence/13-agent-turns.mmd` | How the orchestrator picks a speaker and generates an utterance |
| 14 | `sequence/14-human-interrupt.mmd` | Quiz flow: detection, question, response or timeout |
| 15 | `sequence/15-rag-ingestion.mmd` | Step-by-step URL/file ingestion into ChromaDB |
| 16 | `sequence/16-cicd-pipeline.mmd` | Build and distribution for desktop, web, mobile |

## Keeping Diagrams in Sync

These diagrams reflect the actual implementation in the codebase. When making architectural changes:

1. Update the relevant diagram(s) in the same PR as the code change
2. Each diagram has a `%% Title:` and `%% Description:` comment at the top
3. Keep diagrams under 20 nodes — split into multiple diagrams if needed
4. Use descriptive labels that match actual file/function names in the code
