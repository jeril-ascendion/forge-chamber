import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAppStore } from '../store/app'
import { getSessionList, type SessionSummary } from '../lib/api'
import { AGENTS, PRESET_TOPICS, type AgentKey, AGENT_KEYS } from '../lib/constants'

export default function Dashboard() {
  const navigate = useNavigate()
  const { engineerName, totalXp, setRoom } = useAppStore()
  const [topic, setTopic] = useState('')
  const [selectedAgents, setSelectedAgents] = useState<AgentKey[]>(['sre', 'sys_arch'])
  const [sessions, setSessions] = useState<SessionSummary[]>([])

  useEffect(() => {
    getSessionList().then(setSessions).catch(() => {})
  }, [])

  function toggleAgent(key: AgentKey) {
    setSelectedAgents((prev) =>
      prev.includes(key) ? prev.filter((a) => a !== key) : [...prev, key],
    )
  }

  function handleCreateRoom() {
    if (!topic.trim() || selectedAgents.length < 2) return
    setRoom({ topic: topic.trim(), agents: selectedAgents, userRole: '' })
    navigate('/room/setup')
  }

  const greeting = new Date().getHours() < 12 ? 'Good morning' : new Date().getHours() < 17 ? 'Good afternoon' : 'Good evening'

  return (
    <div className="h-full overflow-y-auto p-6 md:p-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold">{greeting}, {engineerName.split(' ')[0] || 'Engineer'}</h1>
          <p className="text-[var(--text-dim)] text-sm">Ready for your next challenge?</p>
        </div>
        <div className="bg-[var(--bg-card)] border border-[var(--border-dark)] rounded-xl px-5 py-2">
          <span className="text-xs text-[var(--text-dim)]">Total XP</span>
          <div className="text-xl font-bold text-brand">{totalXp}</div>
        </div>
      </div>

      {/* Quick start */}
      <div className="bg-[var(--bg-card)] border border-[var(--border-dark)] rounded-xl p-6 mb-8">
        <h2 className="text-lg font-semibold mb-4">Quick Start</h2>

        <input
          type="text"
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
          placeholder="Enter a debate topic..."
          className="w-full bg-[var(--bg)] border border-[var(--border-dark)] rounded-lg px-4 py-3 text-[var(--text)] focus:outline-none focus:border-brand mb-3"
        />

        <div className="flex gap-2 flex-wrap mb-5">
          {PRESET_TOPICS.map((t) => (
            <button
              key={t}
              onClick={() => setTopic(t)}
              className="px-3 py-1.5 rounded-full text-xs bg-[var(--bg-elevated)] text-[var(--text-dim)] hover:text-[var(--text)] hover:bg-brand/20 transition-colors"
            >
              {t}
            </button>
          ))}
        </div>

        <div className="mb-5">
          <label className="block text-sm text-[var(--text-dim)] mb-2">Select agents (min 2)</label>
          <div className="flex gap-2 flex-wrap">
            {AGENT_KEYS.map((key) => {
              const agent = AGENTS[key]
              const active = selectedAgents.includes(key)
              return (
                <button
                  key={key}
                  onClick={() => toggleAgent(key)}
                  className="px-3 py-2 rounded-lg text-sm font-medium transition-all border"
                  style={{
                    borderColor: active ? agent.color : 'var(--border-dark)',
                    backgroundColor: active ? agent.color + '20' : 'transparent',
                    color: active ? agent.color : 'var(--text-dim)',
                  }}
                >
                  {agent.name} <span className="text-xs opacity-70">{agent.role}</span>
                </button>
              )
            })}
          </div>
        </div>

        <button
          onClick={handleCreateRoom}
          disabled={!topic.trim() || selectedAgents.length < 2}
          className="bg-brand hover:bg-brand/90 disabled:opacity-40 disabled:cursor-not-allowed text-white font-semibold px-8 py-3 rounded-lg transition-colors"
        >
          Create Room
        </button>
      </div>

      {/* Recent sessions */}
      {sessions.length > 0 && (
        <div>
          <h2 className="text-lg font-semibold mb-3">Recent Sessions</h2>
          <div className="space-y-2">
            {sessions.slice(0, 5).map((s) => (
              <button
                key={s.id}
                onClick={() => navigate('/debrief', { state: { sessionId: s.id } })}
                className="w-full bg-[var(--bg-card)] border border-[var(--border-dark)] rounded-lg p-4 text-left hover:border-brand/40 transition-colors"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-sm font-medium">{s.topic || 'Session'}</div>
                    <div className="text-xs text-[var(--text-dim)]">
                      {new Date(s.started_at).toLocaleDateString()}
                    </div>
                  </div>
                  <div className="text-brand font-semibold text-sm">+{s.xp_earned} XP</div>
                </div>
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
