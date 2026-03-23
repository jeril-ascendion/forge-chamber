import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAppStore } from '../store/app'
import { startSession } from '../lib/api'
import { AGENTS, AGENT_KEYS, ROLE_TRACKS, type AgentKey } from '../lib/constants'
import ContextDrop from '../components/ContextDrop'

export default function RoomSetup() {
  const navigate = useNavigate()
  const { topic: savedTopic, agents: savedAgents, setRoom, setSession, setIsDebating } = useAppStore()

  const [topic, setTopic] = useState(savedTopic || '')
  const [selectedAgents, setSelectedAgents] = useState<AgentKey[]>(savedAgents.length ? savedAgents : ['sre', 'sys_arch'])
  const [userRole, setUserRole] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  function toggleAgent(key: AgentKey) {
    setSelectedAgents((prev) =>
      prev.includes(key) ? prev.filter((a) => a !== key) : [...prev, key],
    )
  }

  async function handleStart() {
    if (!topic.trim() || selectedAgents.length < 2) return
    setLoading(true)
    setError('')
    try {
      setRoom({ topic: topic.trim(), agents: selectedAgents, userRole: userRole || 'Engineer' })
      const res = await startSession({
        topic: topic.trim(),
        agents: selectedAgents,
        user_role: userRole || 'Engineer',
      })
      setSession({ sessionId: res.session_id, livekitToken: res.livekit_token, livekitUrl: res.livekit_url })
      setIsDebating(true)
      navigate('/room/active')
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to start session')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="h-full overflow-y-auto p-6 md:p-8">
      <h1 className="text-2xl font-bold mb-6">Room Setup</h1>

      <div className="max-w-2xl space-y-6">
        {error && <div className="bg-accent/20 text-accent px-4 py-2 rounded text-sm">{error}</div>}

        <div>
          <label className="block text-sm text-[var(--text-dim)] mb-1">Debate Topic</label>
          <input
            type="text"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            placeholder="What should the panel debate?"
            className="w-full bg-[var(--bg-card)] border border-[var(--border-dark)] rounded-lg px-4 py-3 focus:outline-none focus:border-brand"
          />
        </div>

        <div>
          <label className="block text-sm text-[var(--text-dim)] mb-2">Select Agents (min 2)</label>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {AGENT_KEYS.map((key) => {
              const agent = AGENTS[key]
              const active = selectedAgents.includes(key)
              return (
                <button
                  key={key}
                  onClick={() => toggleAgent(key)}
                  className="p-4 rounded-xl border text-left transition-all"
                  style={{
                    borderColor: active ? agent.color : 'var(--border-dark)',
                    backgroundColor: active ? agent.color + '15' : 'var(--bg-card)',
                  }}
                >
                  <div className="flex items-center gap-2 mb-1">
                    <div className="w-3 h-3 rounded-full" style={{ backgroundColor: agent.color }} />
                    <span className="font-semibold">{agent.name}</span>
                    <span className="text-xs text-[var(--text-dim)]">{agent.role}</span>
                  </div>
                  <p className="text-xs text-[var(--text-dim)]">{agent.mandate}</p>
                </button>
              )
            })}
          </div>
        </div>

        <div>
          <label className="block text-sm text-[var(--text-dim)] mb-1">Your Role</label>
          <select
            value={userRole}
            onChange={(e) => setUserRole(e.target.value)}
            className="w-full bg-[var(--bg-card)] border border-[var(--border-dark)] rounded-lg px-4 py-2.5 focus:outline-none focus:border-brand"
          >
            <option value="">Select your role...</option>
            {ROLE_TRACKS.map((r) => (
              <option key={r} value={r}>{r}</option>
            ))}
            <option value="Learner">Learner (observing)</option>
          </select>
        </div>

        <div>
          <label className="block text-sm text-[var(--text-dim)] mb-2">Context Sources (optional)</label>
          <ContextDrop />
        </div>

        <button
          onClick={handleStart}
          disabled={!topic.trim() || selectedAgents.length < 2 || loading}
          className="bg-accent hover:bg-accent/90 disabled:opacity-40 disabled:cursor-not-allowed text-white font-semibold px-8 py-3 rounded-lg transition-colors"
        >
          {loading ? 'Starting room...' : 'Start Room'}
        </button>
      </div>
    </div>
  )
}
