import { useNavigate } from 'react-router-dom'
import { useAppStore } from '../store/app'
import SkillRadar from '../components/SkillRadar'

export default function Debrief() {
  const navigate = useNavigate()
  const { topic, debrief, xpEarned, resetSession } = useAppStore()

  const scores = debrief?.scores ?? { technical_depth: 0, communication: 0, debate_resilience: 0, ai_native: 0 }
  const insights = debrief?.key_insights ?? []
  const strongMoments = debrief?.strong_moments ?? []
  const gaps = debrief?.knowledge_gaps ?? []
  const comment = debrief?.overall_comment ?? 'No debrief available.'

  function handleNewRoom() {
    resetSession()
    navigate('/room/setup')
  }

  const scoreLabels = [
    { key: 'technical_depth', label: 'Technical Depth' },
    { key: 'communication', label: 'Communication' },
    { key: 'debate_resilience', label: 'Debate Resilience' },
    { key: 'ai_native', label: 'AI-Native' },
  ]

  return (
    <div className="h-full overflow-y-auto p-6 md:p-8">
      <div className="max-w-3xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-2xl font-bold mb-1">Session Debrief</h1>
          <p className="text-[var(--text-dim)]">{topic || 'Debate session'}</p>
          <div className="mt-3 inline-block bg-brand/20 text-brand font-bold text-xl px-4 py-2 rounded-lg">
            +{xpEarned} XP
          </div>
        </div>

        {/* Score cards + radar */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          <div className="grid grid-cols-2 gap-3">
            {scoreLabels.map(({ key, label }) => (
              <div key={key} className="bg-[var(--bg-card)] border border-[var(--border-dark)] rounded-xl p-4">
                <div className="text-xs text-[var(--text-dim)] mb-1">{label}</div>
                <div className="text-2xl font-bold">{(scores[key] ?? 0).toFixed(1)}</div>
                <div className="text-xs text-[var(--text-dim)]">/ 5.0</div>
              </div>
            ))}
          </div>
          <SkillRadar scores={scores as { technical_depth: number; communication: number; debate_resilience: number; ai_native: number }} />
        </div>

        {/* Key insights */}
        {insights.length > 0 && (
          <div className="mb-6">
            <h2 className="text-lg font-semibold mb-3">Key Insights</h2>
            <ul className="space-y-2">
              {insights.map((insight, i) => (
                <li key={i} className="flex gap-2 text-sm">
                  <span className="text-brand">-</span>
                  <span>{insight}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Strong moments */}
        {strongMoments.length > 0 && (
          <div className="mb-6">
            <h2 className="text-lg font-semibold mb-3">Strong Moments</h2>
            {strongMoments.map((m, i) => (
              <div key={i} className="bg-[var(--bg-card)] border border-[var(--border-dark)] rounded-lg p-3 mb-2 text-sm">
                <span className="text-brand font-medium">Turn {m.turn}: </span>
                {m.observation}
              </div>
            ))}
          </div>
        )}

        {/* Knowledge gaps */}
        {gaps.length > 0 && (
          <div className="mb-6">
            <h2 className="text-lg font-semibold mb-3">Knowledge Gaps</h2>
            {gaps.map((g, i) => (
              <div key={i} className="bg-[var(--bg-card)] border border-[var(--border-dark)] rounded-lg p-3 mb-2 text-sm">
                <div className="font-medium">{g.topic}</div>
                <div className="text-[var(--text-dim)] text-xs mt-1">Study: {g.suggested_study}</div>
              </div>
            ))}
          </div>
        )}

        {/* Overall comment */}
        <div className="mb-8 bg-[var(--bg-card)] border border-[var(--border-dark)] rounded-xl p-5">
          <h2 className="text-lg font-semibold mb-2">Overall Assessment</h2>
          <p className="text-sm leading-relaxed text-[var(--text-dim)]">{comment}</p>
        </div>

        {/* Actions */}
        <div className="flex gap-3">
          <button
            onClick={handleNewRoom}
            className="bg-brand text-white px-6 py-2.5 rounded-lg font-semibold text-sm"
          >
            Start Another Room
          </button>
          <button
            onClick={() => navigate('/dashboard')}
            className="border border-[var(--border-dark)] px-6 py-2.5 rounded-lg text-sm"
          >
            Dashboard
          </button>
        </div>
      </div>
    </div>
  )
}
