import { useCallback, useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Room, RoomEvent } from 'livekit-client'
import { useAppStore } from '../store/app'
import { endSession, type TurnPayload } from '../lib/api'
import { type AgentKey } from '../lib/constants'
import TranscriptFeed from '../components/TranscriptFeed'
import VoiceBar from '../components/VoiceBar'
import AgentPanel from '../components/AgentPanel'

export default function RoomActive() {
  const navigate = useNavigate()
  const {
    topic, agents, sessionId, livekitToken, livekitUrl,
    transcript, quizEvent, addTurn, setActiveSpeaker, setQuizEvent, setDebrief,
    setIsDebating,
  } = useAppStore()

  const [isJoined, setIsJoined] = useState(false)
  const [elapsed, setElapsed] = useState(0)
  const [showEndConfirm, setShowEndConfirm] = useState(false)
  const roomRef = useRef<Room | null>(null)
  const timerRef = useRef<ReturnType<typeof setInterval>>()

  // Session timer
  useEffect(() => {
    timerRef.current = setInterval(() => setElapsed((e) => e + 1), 1000)
    return () => clearInterval(timerRef.current)
  }, [])

  const formatTime = (s: number) =>
    `${String(Math.floor(s / 60)).padStart(2, '0')}:${String(s % 60).padStart(2, '0')}`

  // LiveKit room connection
  useEffect(() => {
    if (!livekitToken || !livekitUrl) return

    const room = new Room()
    roomRef.current = room

    room.on(RoomEvent.DataReceived, (payload: Uint8Array) => {
      try {
        const msg = JSON.parse(new TextDecoder().decode(payload))
        handleDataMessage(msg)
      } catch { /* ignore parse errors */ }
    })

    room.connect(livekitUrl, livekitToken).catch((err) => {
      console.error('LiveKit connect failed:', err)
    })

    return () => {
      room.disconnect()
      roomRef.current = null
    }
  }, [livekitToken, livekitUrl])

  const handleDataMessage = useCallback((msg: Record<string, unknown>) => {
    const type = msg.type as string
    if (type === 'turn_committed') {
      addTurn({
        speaker_type: msg.speaker_type as string,
        speaker_key: msg.speaker_key as string,
        speaker_name: msg.speaker_name as string,
        speaker_role: (msg.speaker_role as string) || '',
        text: msg.text as string,
        turn_number: msg.turn_number as number,
        is_quiz_event: false,
      })
    } else if (type === 'speaker_change') {
      setActiveSpeaker(msg.agent_key as string)
    } else if (type === 'quiz_event') {
      setQuizEvent({
        question: msg.question as string,
        agent_key: msg.agent_key as string,
        timeout_seconds: (msg.timeout_seconds as number) || 30,
      })
    } else if (type === 'session_complete') {
      const debrief = msg.debrief as Record<string, unknown>
      const xp = msg.xp as Record<string, unknown>
      if (debrief && xp) {
        setDebrief(debrief as ReturnType<typeof useAppStore.getState>['debrief'] & object, (xp as { total: number }).total)
      }
      navigate('/debrief')
    }
  }, [addTurn, setActiveSpeaker, setQuizEvent, setDebrief, navigate])

  // For web-only mode (no LiveKit), simulate with polling
  // In production, all data comes via LiveKit data channel above

  function handleJoin() {
    setIsJoined(true)
    // Enable mic via LiveKit room
    roomRef.current?.localParticipant?.setMicrophoneEnabled(true)
  }

  function handleLeave() {
    setIsJoined(false)
    roomRef.current?.localParticipant?.setMicrophoneEnabled(false)
  }

  async function handleEndSession() {
    setShowEndConfirm(false)
    setIsDebating(false)
    clearInterval(timerRef.current)

    try {
      const turns: TurnPayload[] = transcript.map((t) => ({
        speaker_type: t.speaker_type,
        speaker_key: t.speaker_key,
        speaker_name: t.speaker_name,
        text: t.text,
        turn_number: t.turn_number,
        is_quiz_event: t.is_quiz_event,
      }))
      const result = await endSession(sessionId, turns)
      setDebrief(
        result.debrief as ReturnType<typeof useAppStore.getState>['debrief'] & object,
        result.xp_earned,
      )
    } catch (err) {
      console.error('End session failed:', err)
    }

    navigate('/debrief')
  }

  return (
    <div className="flex h-full">
      {/* Left panel */}
      <div className="w-[280px] bg-[var(--bg-card)] border-r border-[var(--border-dark)] flex flex-col p-4">
        <div className="mb-4">
          <h2 className="text-sm font-semibold truncate">{topic || 'Debate'}</h2>
          <div className="text-2xl font-mono text-brand mt-1">{formatTime(elapsed)}</div>
        </div>

        <div className="flex-1" />

        <button
          onClick={() => setShowEndConfirm(true)}
          className="w-full py-2 border border-accent text-accent rounded-lg text-sm hover:bg-accent/10 transition-colors"
        >
          End Session
        </button>

        {/* End confirmation dialog */}
        {showEndConfirm && (
          <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50">
            <div className="bg-[var(--bg-card)] rounded-xl p-6 max-w-sm border border-[var(--border-dark)]">
              <h3 className="text-lg font-semibold mb-2">End this session?</h3>
              <p className="text-sm text-[var(--text-dim)] mb-4">
                The debate will stop and your debrief will be generated.
              </p>
              <div className="flex gap-3">
                <button
                  onClick={() => setShowEndConfirm(false)}
                  className="flex-1 py-2 border border-[var(--border-dark)] rounded-lg text-sm"
                >
                  Cancel
                </button>
                <button
                  onClick={handleEndSession}
                  className="flex-1 py-2 bg-accent text-white rounded-lg text-sm"
                >
                  End Session
                </button>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Center — transcript + voice bar */}
      <div className="flex-1 flex flex-col overflow-hidden">
        <TranscriptFeed />
        <VoiceBar onJoin={handleJoin} onLeave={handleLeave} isJoined={isJoined} maxTurns={20} />
      </div>

      {/* Right panel */}
      <div className="w-[300px] bg-[var(--bg-card)] border-l border-[var(--border-dark)] p-4 overflow-y-auto">
        <AgentPanel agentKeys={agents as AgentKey[]} />

        {/* Quiz zone */}
        {quizEvent && (
          <div className="mt-4 p-4 rounded-xl border-2 border-yellow-600/50 bg-yellow-900/20">
            <div className="text-xs text-yellow-400 uppercase tracking-wider mb-2">Question for you</div>
            <p className="text-sm mb-3">{quizEvent.question}</p>
            <button
              onClick={() => setQuizEvent(null)}
              className="text-xs text-[var(--text-dim)] hover:text-[var(--text)]"
            >
              Skip
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
