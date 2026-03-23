import { useEffect } from 'react'
import { useAppStore } from '../store/app'
import { AGENTS } from '../lib/constants'

interface VoiceBarProps {
  onJoin: () => void
  onLeave: () => void
  isJoined: boolean
  maxTurns: number
}

export default function VoiceBar({ onJoin, onLeave, isJoined, maxTurns }: VoiceBarProps) {
  const { activeSpeaker, transcript } = useAppStore()
  const agent = activeSpeaker ? AGENTS[activeSpeaker as keyof typeof AGENTS] : null
  const turnCount = transcript.length

  // Spacebar shortcut
  useEffect(() => {
    function handleKeyDown(e: KeyboardEvent) {
      if (e.code === 'Space' && e.target === document.body) {
        e.preventDefault()
        isJoined ? onLeave() : onJoin()
      }
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [isJoined, onJoin, onLeave])

  return (
    <div className="h-16 bg-[var(--bg-card)] border-t border-[var(--border-dark)] flex items-center px-4 gap-4">
      {/* Speaker info + waveform */}
      <div className="flex items-center gap-3 min-w-[200px]">
        {activeSpeaker && agent ? (
          <>
            <div className="flex gap-1 items-end h-6">
              {[0, 1, 2, 3].map((i) => (
                <div
                  key={i}
                  className="w-1 bg-brand rounded-full"
                  style={{
                    animation: `wave 0.8s ease-in-out ${i * 0.15}s infinite`,
                    height: '8px',
                  }}
                />
              ))}
            </div>
            <div>
              <div className="text-sm font-medium" style={{ color: agent.color }}>{agent.name}</div>
              <div className="text-xs text-[var(--text-dim)]">{agent.role}</div>
            </div>
          </>
        ) : (
          <div className="text-xs text-[var(--text-dim)]">Listening...</div>
        )}
      </div>

      {/* Turn counter */}
      <div className="flex-1 text-center text-xs text-[var(--text-dim)]">
        Turn {turnCount} / {maxTurns}
      </div>

      {/* Join/Leave button */}
      <button
        onClick={isJoined ? onLeave : onJoin}
        className={`px-6 py-2 rounded-lg font-semibold text-sm transition-all ${
          isJoined
            ? 'bg-green-600 text-white animate-pulse'
            : 'bg-brand text-white hover:bg-brand/90'
        }`}
      >
        {isJoined ? "You're speaking..." : 'Join Debate'}
      </button>
    </div>
  )
}
