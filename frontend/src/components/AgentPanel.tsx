import { useAppStore } from '../store/app'
import { AGENTS, type AgentKey } from '../lib/constants'

export default function AgentPanel({ agentKeys }: { agentKeys: AgentKey[] }) {
  const activeSpeaker = useAppStore((s) => s.activeSpeaker)

  return (
    <div className="space-y-2">
      <h3 className="text-xs text-[var(--text-dim)] uppercase tracking-wider mb-2">Panel</h3>
      {agentKeys.map((key) => {
        const agent = AGENTS[key]
        if (!agent) return null
        const isActive = activeSpeaker === key
        return (
          <div
            key={key}
            className="flex items-center gap-3 p-3 rounded-lg transition-all"
            style={{
              backgroundColor: isActive ? agent.color + '15' : 'var(--bg-card)',
              border: isActive ? `2px solid ${agent.color}` : '2px solid transparent',
              animation: isActive ? 'pulse-ring 1.5s infinite' : 'none',
            }}
          >
            <div
              className="w-8 h-8 rounded-full flex items-center justify-center text-white text-xs font-bold"
              style={{ backgroundColor: agent.color }}
            >
              {agent.name[0]}
            </div>
            <div>
              <div className="text-sm font-medium">{agent.name}</div>
              <div className="text-xs text-[var(--text-dim)]">{agent.role}</div>
            </div>
            {isActive && (
              <div className="ml-auto w-2 h-2 rounded-full bg-green-400 animate-pulse" />
            )}
          </div>
        )
      })}
    </div>
  )
}
