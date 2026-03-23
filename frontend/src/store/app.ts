import { create } from 'zustand'
import type { AgentKey } from '../lib/constants'

export interface TranscriptTurn {
  speaker_type: string
  speaker_key: string
  speaker_name: string
  speaker_role: string
  text: string
  turn_number: number
  is_quiz_event: boolean
  timestamp?: string
}

export interface DebriefData {
  key_insights: string[]
  strong_moments: { turn: number; observation: string }[]
  knowledge_gaps: { topic: string; suggested_study: string }[]
  scores: Record<string, number>
  overall_comment: string
}

interface AppState {
  // Engineer
  engineerId: string
  engineerName: string
  roleTrack: string
  skillLevel: string
  totalXp: number
  totalSessions: number
  setEngineer: (data: { id: string; name: string; role_track: string; skill_level: string; total_xp: number; total_sessions: number }) => void

  // Room
  topic: string
  agents: AgentKey[]
  userRole: string
  sessionId: string
  livekitToken: string
  livekitUrl: string
  setRoom: (data: { topic: string; agents: AgentKey[]; userRole: string }) => void
  setSession: (data: { sessionId: string; livekitToken: string; livekitUrl: string }) => void

  // Active session
  transcript: TranscriptTurn[]
  activeSpeaker: string | null
  isDebating: boolean
  quizEvent: { question: string; agent_key: string; timeout_seconds: number } | null
  debrief: DebriefData | null
  xpEarned: number
  xpBreakdown: Record<string, number> | null
  newBadges: string[]
  addTurn: (turn: TranscriptTurn) => void
  setActiveSpeaker: (key: string | null) => void
  setIsDebating: (v: boolean) => void
  setQuizEvent: (e: { question: string; agent_key: string; timeout_seconds: number } | null) => void
  setDebrief: (d: DebriefData, xp: number, breakdown?: Record<string, number> | null, badges?: string[]) => void
  resetSession: () => void
}

export const useAppStore = create<AppState>((set) => ({
  // Engineer defaults
  engineerId: '',
  engineerName: '',
  roleTrack: '',
  skillLevel: 'mid',
  totalXp: 0,
  totalSessions: 0,
  setEngineer: (data) =>
    set({
      engineerId: data.id,
      engineerName: data.name,
      roleTrack: data.role_track,
      skillLevel: data.skill_level,
      totalXp: data.total_xp,
      totalSessions: data.total_sessions,
    }),

  // Room defaults
  topic: '',
  agents: [],
  userRole: '',
  sessionId: '',
  livekitToken: '',
  livekitUrl: '',
  setRoom: (data) => set({ topic: data.topic, agents: data.agents, userRole: data.userRole }),
  setSession: (data) =>
    set({ sessionId: data.sessionId, livekitToken: data.livekitToken, livekitUrl: data.livekitUrl }),

  // Session defaults
  transcript: [],
  activeSpeaker: null,
  isDebating: false,
  quizEvent: null,
  debrief: null,
  xpEarned: 0,
  xpBreakdown: null,
  newBadges: [],
  addTurn: (turn) => set((s) => ({ transcript: [...s.transcript, turn] })),
  setActiveSpeaker: (key) => set({ activeSpeaker: key }),
  setIsDebating: (v) => set({ isDebating: v }),
  setQuizEvent: (e) => set({ quizEvent: e }),
  setDebrief: (d, xp, breakdown, badges) => set({ debrief: d, xpEarned: xp, xpBreakdown: breakdown ?? null, newBadges: badges ?? [] }),
  resetSession: () =>
    set({
      transcript: [],
      activeSpeaker: null,
      isDebating: false,
      quizEvent: null,
      debrief: null,
      xpEarned: 0,
      xpBreakdown: null,
      newBadges: [],
      sessionId: '',
      livekitToken: '',
      livekitUrl: '',
    }),
}))
