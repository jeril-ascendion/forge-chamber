# Forge Chamber — UI Design Specification

> This document describes every screen, component, and interaction for Forge Chamber.
> It is written for Google Stitch to generate UI wireframes and mockups.
> Each screen section includes layout description, component list, and visual intent.

---

## Design Language

### Core Aesthetic
Forge Chamber should feel like a **professional tool used by experts** — not a consumer app, not a gamified learning platform. Think: the visual density and restraint of Linear or Vercel's dashboard, with warmth added through the agent color system. Dark surfaces dominant because engineers are typically in low-light environments.

### Color Palette

```
Background Primary:    #0F0F14   (near-black, main surfaces)
Background Secondary:  #1A1A24   (card surfaces, panels)
Background Tertiary:   #252535   (hover states, inputs)
Border:                rgba(255,255,255,0.10)

Text Primary:          #F0EEF8   (white with slight warmth)
Text Secondary:        #9A99B0   (muted labels, captions)
Text Tertiary:         #55546A   (disabled, hint text)

Brand Blue:            #2B5EA7   (primary actions, links)
Accent Orange:         #E8533A   (alerts, emphasis)

Agent SRE:             #E8533A   (coral/red)
Agent Architect:       #4A7CC7   (blue)
Agent Cloud:           #1D9E75   (teal/green)
Agent Java:            #D4890A   (amber)
Agent UI Dev:          #8B7FE8   (purple)
Agent Human:           #3AAA5A   (green — the user's voice)
```

### Typography
- **Headings:** Inter or system-ui, weight 600, tight tracking
- **Body:** Inter or system-ui, weight 400, relaxed line height
- **Code / technical:** JetBrains Mono or Fira Code, weight 400
- **Agent names:** weight 600, colored per agent
- **No serif fonts anywhere**

### Layout Principles
- App window: 1200×800 minimum, responsive down to 900×600
- Left panel: 280px fixed (navigation + context)
- Main content: flex-fill
- Right panel: 320px fixed (appears only in active Room)
- All panels separated by subtle 1px borders, no heavy shadows

---

## Screen 1: Splash Screen

**Purpose:** Shown for 4 seconds while Python sidecar initializes.

**Layout:**
- Full window, centered content
- Background: `#0F0F14`

**Elements:**
- Center: App logo mark (a stylized hexagonal chamber shape, white/brand blue)
- Below logo: "Forge Chamber" in 32px, weight 600, white
- Below name: "Where engineers get tested" in 14px, text-secondary color
- Bottom: thin progress bar (animated, brand blue, full width) showing loading state
- Bottom center: "Starting engine..." in 12px text-tertiary

**Visual intent:** Clean, minimal, professional. Feels like VS Code or Linear loading.

---

## Screen 2: Onboarding — First Launch

**Purpose:** Collect engineer profile and API keys on first run only.

**Layout:**
- Full window, two-column
- Left column (400px): Visual/brand panel
- Right column (fill): Form

**Left column:**
- Background: brand blue (#2B5EA7)
- Large "FC" monogram in white, 80px
- Below: "Forge Chamber" 24px white
- Below: "Engineering excellence, built through debate." 14px, light blue
- Bottom: Three small feature pills: "Voice-first" / "Multi-agent debate" / "Skill tracking"

**Right column:**
- White/light background (contrast with left)
- Heading: "Set up your profile" 24px
- Subheading: "We only ask once. Everything is stored locally." 13px text-secondary
- Form sections (each collapsible with ▶ expand):

  **Your profile:**
  - Name input (text)
  - Role track dropdown: UI Developer / Java Developer / Cloud Engineer / Solutions Architect / SRE
  - Experience level: Junior (0–2yr) / Mid (2–5yr) / Senior (5yr+) — radio buttons

  **API Keys** (each field has a show/hide toggle and a "?" info link):
  - Anthropic API Key
  - LiveKit URL
  - LiveKit API Key
  - LiveKit API Secret
  - Deepgram API Key
  - Cartesia API Key
  
  - "Where do I get these?" link — opens external browser

- CTA: "Enter the Chamber" button — full width, brand blue, 48px height
- Below button: "All keys are stored in your system keychain. Never in plaintext." 11px text-tertiary

---

## Screen 3: Dashboard (Home)

**Purpose:** Main hub — shows profile, recent sessions, quick-start.

**Layout:**
- Narrow left sidebar (64px) — icon navigation only
- Main content area (fill)
- No right panel

**Left Sidebar:**
- Top: App icon (small hexagon logo mark)
- Nav icons (with tooltips on hover):
  - Home (active state)
  - New Room (+ icon)
  - Session History (clock icon)
  - Progress / Skills (radar chart icon)
  - Settings (gear icon)
- Bottom: Engineer initials avatar (opens profile)

**Main Content — Three Zones:**

**Zone 1: Header bar (48px)**
- Left: "Good morning, [Name]" or time-of-day greeting
- Right: Total XP counter (animated number) + streak badge if applicable

**Zone 2: Quick Start (prominent, above fold)**
- Heading: "Start a new Room" (18px)
- Large topic input field (full width, 48px height, placeholder: "What do you want to debate today?")
- Below input: Curated topic pills — scrollable horizontal row:
  - "High-volume AWS architecture"
  - "React Native security layer"
  - "Microservices migration strategy"
  - "Real-time notification system"
  - "Kubernetes vs ECS"
  - (etc.)
- Agent quick-select: "Who joins the Room?" — row of 5 agent pills (click to toggle):
  - [SRE Alex] [Maya SA] [Ravi Cloud] [Sam Java] [Jordan UI]
  - Each shows agent color, name, role abbreviation
  - Selected agents show filled background, unselected show ghost/outline
- "Create Room" button — brand blue, large

**Zone 3: Recent Sessions (scrollable)**
- Heading: "Recent sessions" (16px) + "View all" link
- Session cards (horizontal scroll or 2-column grid):
  Each card shows:
  - Topic (truncated to 1 line)
  - Agents who participated (colored dots)
  - Date + duration
  - XP earned
  - Skill scores as mini 4-bar visual
  - "Replay transcript" link

---

## Screen 4: Room Setup (Full Configuration)

**Purpose:** Detailed Room configuration before starting a session.

**Layout:**
- Wide centered panel (max 800px) — no sidebars
- Stepped form with 4 steps shown in progress bar at top:
  `Topic → Agents → Your Role → Context → Start`

**Step 1: Topic**
- Large textarea: "What's the debate topic?" — 120px height, big font
- Below: "Or pick from our library" — 3-column grid of scenario cards
  Each scenario card: title, 2 agent icons, difficulty badge (Intermediate/Advanced)
- Selected scenario: highlighted with brand blue border

**Step 2: Agent Selection**
- Heading: "Who's in the room?"
- 5 large agent cards in a grid (2+2+1 layout):
  Each card shows:
  - Agent name (large, colored)
  - Role title
  - 3-bullet mandate summary
  - Communication style badge (e.g. "Direct", "Socratic", "Methodical")
  - Toggle checkbox top-right
  - "2 minimum" validation shown if <2 selected
  
**Step 3: Your Role**
- "Which role will you play in this debate?"
- Role selector: same 5 roles + custom "Learner (no specific role)"
- Skill level selector for your role: Junior / Mid / Senior
- Note: "Agents will calibrate their expectations to your level."

**Step 4: Context (optional)**
- Section header: "Give the agents context" + "(optional)" badge
- URL input with "Add" button → shows ingested chip below on success
- File drop zone: large dashed rectangle with "Drop PDF, DOCX, TXT, or Markdown here" + "Browse files" link
- Voice note: microphone button + "Record up to 2 minutes of context"
- Ingested sources list: each source shows name, chunk count, delete X

**Footer:**
- "Back" ghost button + "Start Room" filled button (disabled until topic + 2 agents selected)

---

## Screen 5: Room Active — Listen Mode

**Purpose:** The main debate experience. Agent-to-agent discussion with user watching.

**Layout:**
- Left panel (280px): Room info + context sources + controls
- Center (fill): Transcript feed
- Right panel (320px): Agent cards + quiz area

**Left Panel:**
- Room name (editable on click)
- Topic (truncated, full on hover)
- Session timer (MM:SS counting up)
- "Context" section: mini list of ingested sources
- "End Session" button (ghost, with warning dialog)
- Mute/Unmute mic toggle
- Volume slider

**Center — Transcript Feed:**
- Scrolling chronological list of Turn cards
- Each Turn card:
  - Colored left border (agent color)
  - Agent name (bold, colored) + role (muted)
  - Turn text (readable, 15px)
  - Timestamp (right-aligned, small)
- Human turns: green left border + "You" label + slightly different background
- Quiz Event turns: amber border + amber "You were asked" badge at top
- Unanswered quiz: faded "You didn't answer — agent responded:" prefix
- Auto-scrolls to bottom as turns arrive
- "New messages ↓" floating button when user has scrolled up

**Bottom: Voice Bar** (full width, 64px height, floats above transcript)
- Background: slightly elevated surface
- Left: Speaker indicator
  - Animated waveform (4 vertical bars, CSS animation)
  - "[Agent Name] — [Role]" text
  - Agent color dot
- Center: Debate progress indicator (e.g. Turn 7 of ~20)
- Right: Large "Join Debate" button
  - State 1 (Listen Mode): Green, text "Join Debate"
  - State 2 (Speaking): Red pulse, text "You're speaking..." 
  - State 3 (Processing): Spinner, text "Processing..."

**Right Panel — Agent Cards:**
- Heading: "In the room"
- 5 stacked compact agent cards:
  Each card:
  - Colored left stripe
  - Name + role
  - Status indicator: Active (animated ring) / Listening / Idle
  - Speaking: card expands slightly, background lightens
- Below agents: Quiz zone (appears only during Quiz Event)
  - Card with amber background
  - "Alex (SRE) is asking you:" + question text
  - 30s countdown ring animation
  - "Respond" prompt
  - "Skip this question" link

---

## Screen 6: Room Active — Debate Mode (User Speaking)

**Purpose:** State when user has joined and is speaking.

**Changes from Listen Mode:**
- Voice Bar: background becomes green tint, "You're speaking..." with mic waveform
- Right panel: "Your turn" card appears at top — shows mic level, "Speaking..." status
- Transcript: new "You" turn card added at bottom in real-time as speech is transcribed
- All agent cards show "Listening" status
- "Step back" button replaces "Join Debate"

---

## Screen 7: Session Debrief

**Purpose:** Post-session structured feedback screen.

**Layout:**
- Centered content (max 720px), no sidebars
- Header + 4 content cards + CTA

**Header:**
- "Session complete" (24px)
- Topic shown below
- Duration + XP earned (+[n] XP — animated counting up)

**Card 1: Skill Scores**
- 4-column grid, each column:
  - Domain name (Technical Depth / Communication / Debate Resilience / AI-Native)
  - Large score number (1–5) in brand color
  - Small delta from previous session (+0.3 ↑ or -0.1 ↓)
- SkillRadar SVG below the scores — shows this session vs previous average

**Card 2: Key Insights from the Debate**
- Heading: "What came out of this session"
- 3 bullet points (LLM-generated)

**Card 3: Moments That Stood Out**
- Green section: "Where you reasoned well" — 2–3 transcript excerpts (clickable, shows full turn)
- Amber section: "Knowledge gaps identified" — 2–3 topics + suggested study resources

**Card 4: Overall Assessment**
- Single paragraph (LLM-generated), honest and direct
- Attributed: "— Forge Chamber Analysis"

**CTA row:**
- "Start another room" (brand blue, primary)
- "View full transcript" (ghost)
- "Export debrief" (ghost)

---

## Screen 8: Progress & Skills

**Purpose:** Engineer's longitudinal skill profile.

**Layout:**
- Left sidebar (64px icon nav, same as Dashboard)
- Main content (fill), no right panel

**Content Sections:**

**Section 1: Profile Header**
- Engineer name + role track badge
- Total XP (large, animated)
- Sessions completed
- Streak indicator (flame icon + "5 day streak")

**Section 2: Skill Radar (large)**
- SVG radar chart, 300×300px
- 4 axes, scores plotted
- Shows "This week" vs "All time" toggle
- Each axis labeled at tip

**Section 3: Domain Breakdown**
- 4 horizontal bar charts, one per skill domain
- Each bar: domain name, score bar (colored), score number
- Small note below each: "Based on [n] sessions"

**Section 4: Session History**
- Table view of all sessions:
  | Date | Topic | Duration | XP | Scores (mini bars) | |
  - Click row → opens transcript replay
- "Load more" pagination

**Section 5: Badges** (compact grid)
- Earned: full color, name, date earned
- Locked: grayscale, "?" tooltip showing unlock condition

---

## Screen 9: Settings

**Purpose:** API key management, preferences, about.

**Layout:**
- Centered form (max 600px)

**Sections:**
- **Profile:** Name, role track, skill level (editable)
- **API Keys:** Each key with masked display + "Update" button + link to service
- **Preferences:** 
  - Agent speaking speed (slider: slow / normal / fast)
  - Auto-join after quiz timeout (toggle)
  - Session auto-save (toggle, on by default)
  - Theme: Dark / Light / System (Dark is default + recommended)
- **About:** Version number, GitHub link, license

---

## Component Specifications for Google Stitch

### VoiceBar States
Stitch should generate 3 variants:
1. **Idle** — no one speaking, "Join Debate" button inactive
2. **Agent Speaking** — waveform animated, agent name shown, button active
3. **User Speaking** — green tint, "You're speaking", waveform on left

### Agent Card States
Stitch should generate 3 variants:
1. **Idle** — flat card
2. **Active/Speaking** — animated border ring, expanded
3. **Selected** (Room Setup) — filled background, checkmark

### Turn Card Variants
Stitch should generate 5 variants:
1. **Agent Turn** — colored left border
2. **Human Turn** — green border, different background
3. **Quiz Event** — amber border, amber badge
4. **Unanswered Quiz** — faded, agent-answered prefix
5. **System Message** — neutral, centered, italic

### Transition Animations
- Screen → Screen: 200ms fade
- Turn card enters: slide up from bottom, 150ms
- Agent card active: border ring pulse, continuous
- XP counter: count-up animation, 1s
- Skill radar: polygon morphs on data change, 600ms ease

---

## Accessibility Notes

- All controls keyboard navigable (Tab order logical)
- Spacebar: toggle Join/Leave Debate in active Room
- ESC: exit Debate Mode back to Listen
- All agent names + roles announced via aria-live region when speaker changes
- Transcript text always readable regardless of audio state
- Color is never the only indicator — always paired with shape or text label
- Minimum tap target: 44×44px for all interactive elements
