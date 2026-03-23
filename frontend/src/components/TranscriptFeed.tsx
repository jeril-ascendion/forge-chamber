import { useEffect, useRef, useState } from 'react'
import { useAppStore, type TranscriptTurn } from '../store/app'
import { AGENTS } from '../lib/constants'

function TurnCard({ turn }: { turn: TranscriptTurn }) {
  const isHuman = turn.speaker_type === 'human'
  const isQuiz = turn.is_quiz_event
  const agent = AGENTS[turn.speaker_key as keyof typeof AGENTS]
  const color = isHuman ? 'var(--agent-human)' : isQuiz ? '#D4A017' : agent?.color ?? 'var(--brand)'

  return (
    <div className="flex gap-3 px-4 py-3" style={{ borderLeft: `3px solid ${color}` }}>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-1">
          <span className="text-sm font-semibold" style={{ color }}>
            {isHuman ? 'You' : turn.speaker_name}
          </span>
          {!isHuman && (
            <span className="text-xs text-[var(--text-dim)]">{turn.speaker_role}</span>
          )}
          {isQuiz && (
            <span className="text-xs bg-yellow-900/40 text-yellow-300 px-2 py-0.5 rounded">Quiz</span>
          )}
          <span className="text-xs text-[var(--text-dim)] ml-auto">Turn {turn.turn_number}</span>
        </div>
        <div className="text-sm leading-relaxed whitespace-pre-wrap">
          {isQuiz && <span className="text-yellow-400 font-medium">You were asked: </span>}
          {turn.text}
        </div>
      </div>
    </div>
  )
}

export default function TranscriptFeed() {
  const transcript = useAppStore((s) => s.transcript)
  const containerRef = useRef<HTMLDivElement>(null)
  const [autoScroll, setAutoScroll] = useState(true)
  const prevLength = useRef(0)

  useEffect(() => {
    if (autoScroll && containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight
    }
  }, [transcript.length, autoScroll])

  function handleScroll() {
    if (!containerRef.current) return
    const { scrollTop, scrollHeight, clientHeight } = containerRef.current
    const atBottom = scrollHeight - scrollTop - clientHeight < 60
    setAutoScroll(atBottom)
  }

  const hasNew = !autoScroll && transcript.length > prevLength.current
  useEffect(() => {
    prevLength.current = transcript.length
  }, [transcript.length])

  return (
    <div className="relative flex-1 overflow-hidden">
      <div
        ref={containerRef}
        onScroll={handleScroll}
        className="h-full overflow-y-auto space-y-1 py-2"
      >
        {transcript.length === 0 && (
          <div className="flex items-center justify-center h-full text-[var(--text-dim)] text-sm">
            Waiting for debate to start...
          </div>
        )}
        {transcript.map((turn, i) => (
          <TurnCard key={i} turn={turn} />
        ))}
      </div>

      {hasNew && (
        <button
          onClick={() => {
            setAutoScroll(true)
            containerRef.current?.scrollTo({ top: containerRef.current.scrollHeight, behavior: 'smooth' })
          }}
          className="absolute bottom-4 left-1/2 -translate-x-1/2 bg-brand text-white text-xs px-4 py-1.5 rounded-full shadow-lg"
        >
          New messages ↓
        </button>
      )}
    </div>
  )
}
