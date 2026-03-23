import { useAppStore } from '../store/app'
import { getSession, getSessionList, endSession as apiEndSession, type TurnPayload, type SessionSummary } from '../lib/api'

export function useSession() {
  const { sessionId, transcript, setDebrief, resetSession } = useAppStore()

  async function loadSession(id: string) {
    return getSession(id)
  }

  async function listSessions(): Promise<SessionSummary[]> {
    return getSessionList()
  }

  async function endCurrentSession() {
    if (!sessionId) return null
    const turns: TurnPayload[] = transcript.map((t) => ({
      speaker_type: t.speaker_type,
      speaker_key: t.speaker_key,
      speaker_name: t.speaker_name,
      text: t.text,
      turn_number: t.turn_number,
      is_quiz_event: t.is_quiz_event,
    }))
    const result = await apiEndSession(sessionId, turns)
    setDebrief(
      result.debrief as unknown as Parameters<typeof setDebrief>[0],
      result.xp_earned,
    )
    return result
  }

  return { sessionId, loadSession, listSessions, endCurrentSession, resetSession }
}
