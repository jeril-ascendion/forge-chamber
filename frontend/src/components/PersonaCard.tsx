import type { AgentKey } from '../lib/constants'
import { AGENTS } from '../lib/constants'

interface PersonaCardProps {
  agentKey: AgentKey
  selected: boolean
  onToggle: () => void
}

export default function PersonaCard({ agentKey, selected, onToggle }: PersonaCardProps) {
  const agent = AGENTS[agentKey]
  if (!agent) return null

  return (
    <button
      onClick={onToggle}
      className="p-4 rounded-xl border text-left transition-all w-full"
      style={{
        borderColor: selected ? agent.color : 'var(--border-dark)',
        backgroundColor: selected ? agent.color + '15' : 'var(--bg-card)',
      }}
    >
      <div className="flex items-center gap-2 mb-1">
        <div
          className="w-8 h-8 rounded-full flex items-center justify-center text-white text-xs font-bold"
          style={{ backgroundColor: agent.color }}
        >
          {agent.name[0]}
        </div>
        <div>
          <span className="font-semibold">{agent.name}</span>
          <span className="text-xs text-[var(--text-dim)] ml-2">{agent.role}</span>
        </div>
      </div>
      <p className="text-xs text-[var(--text-dim)] mt-1">{agent.mandate}</p>
    </button>
  )
}
