const BASE_URL = window.electronAPI
  ? 'http://localhost:8765'
  : (import.meta.env.VITE_API_URL ?? 'http://localhost:8765')

export async function apiFetch<T>(path: string, opts?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...opts,
  })
  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(body.detail || `API ${res.status}: ${path}`)
  }
  return res.json()
}

// Health
export const getHealth = () => apiFetch<{ status: string; version: string }>('/health')

// Engineer
export interface EngineerProfile {
  id: string
  name: string
  role_track: string
  skill_level: string
  total_xp: number
  total_sessions: number
}

export const setupEngineer = (data: { name: string; role_track: string; skill_level: string }) =>
  apiFetch<EngineerProfile>('/engineer/setup', { method: 'POST', body: JSON.stringify(data) })

export const getProfile = () => apiFetch<EngineerProfile>('/engineer/profile')

export const updateProfile = (data: Partial<{ name: string; role_track: string; skill_level: string }>) =>
  apiFetch<EngineerProfile>('/engineer/profile', { method: 'PUT', body: JSON.stringify(data) })

// Session
export interface SessionStartResponse {
  livekit_url: string
  livekit_token: string
  room_name: string
  session_id: string
}

export interface SessionDetail {
  id: string
  room_id: string
  engineer_id: string
  started_at: string
  ended_at: string | null
  duration_seconds: number | null
  xp_earned: number
  transcript: string | null
  debrief: string | null
  technical_depth_score: number | null
  communication_score: number | null
  debate_resilience_score: number | null
  ai_native_score: number | null
}

export interface SessionSummary {
  id: string
  started_at: string
  ended_at: string | null
  xp_earned: number
  topic?: string
}

export const startSession = (data: { topic: string; agents: string[]; user_role: string }) =>
  apiFetch<SessionStartResponse>('/session/start', { method: 'POST', body: JSON.stringify(data) })

export const getSession = (id: string) => apiFetch<SessionDetail>(`/session/${id}`)

export const getSessionList = () => apiFetch<SessionSummary[]>('/session/list')

export interface TurnPayload {
  speaker_type: string
  speaker_key?: string
  speaker_name?: string
  text: string
  turn_number: number
  is_quiz_event?: boolean
}

export const endSession = (id: string, transcript: TurnPayload[]) =>
  apiFetch<{ debrief: Record<string, unknown>; scores: Record<string, number>; xp_earned: number; xp_breakdown: Record<string, number> | null; new_badges: string[] }>(
    `/session/${id}/end`,
    { method: 'POST', body: JSON.stringify({ transcript }) },
  )

// RAG
export interface IngestResponse { status: string; chunks: number; title: string }
export interface RagSource { id: string; label: string; chunks: number; ingested_at: string }

export const ingestUrl = (url: string) =>
  apiFetch<IngestResponse>('/rag/ingest-url', { method: 'POST', body: JSON.stringify({ url }) })

export const ingestFile = async (file: File): Promise<IngestResponse> => {
  const form = new FormData()
  form.append('file', file)
  const res = await fetch(`${BASE_URL}/rag/ingest-file`, { method: 'POST', body: form })
  if (!res.ok) throw new Error(`Upload failed: ${res.status}`)
  return res.json()
}

export const getSources = () => apiFetch<RagSource[]>('/rag/sources')
export const deleteSource = (id: string) => apiFetch<{ status: string }>(`/rag/source/${id}`, { method: 'DELETE' })

// Progress
export interface SkillScores {
  technical_depth: number
  communication: number
  debate_resilience: number
  ai_native: number
}

export interface SessionProgress {
  session_id: string
  date: string
  topic: string | null
  duration_seconds: number | null
  xp: number
  scores: Record<string, number | null>
}

export interface BadgeInfo {
  key: string
  label: string
  description: string
  icon: string
  earned_at: string
}

export interface ProgressSummary {
  skills: SkillScores
  total_xp: number
  total_sessions: number
  current_streak: number
  badges: BadgeInfo[]
}

export const getSkills = () => apiFetch<SkillScores>('/progress/skills')
export const getProgressSessions = () => apiFetch<SessionProgress[]>('/progress/sessions')
export const getProgressSummary = () => apiFetch<ProgressSummary>('/progress/summary')
