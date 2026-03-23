import { useEffect, useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { useAppStore, type DebriefData } from '../store/app'
import { getSession } from '../lib/api'
import SkillRadar from '../components/SkillRadar'

export default function Debrief() {
  const navigate = useNavigate()
  const location = useLocation()
  const { topic: storeTopic, debrief: storeDebrief, xpEarned: storeXp, resetSession } = useAppStore()

  // Allow loading a historical session via router state
  const routerSessionId = (location.state as { sessionId?: string } | null)?.sessionId
  const [loading, setLoading] = useState(false)
  const [historicalDebrief, setHistoricalDebrief] = useState<DebriefData | null>(null)
  const [historicalXp, setHistoricalXp] = useState(0)
  const [historicalTopic] = useState('')

  useEffect(() => {
    if (!routerSessionId) return
    // If we already have debrief in store (just finished a session), skip fetch
    if (storeDebrief) return

    setLoading(true)
    getSession(routerSessionId)
      .then((session) => {
        if (session.debrief) {
          try {
            const parsed = JSON.parse(session.debrief) as DebriefData
            setHistoricalDebrief(parsed)
            setHistoricalXp(session.xp_earned)
          } catch { /* debrief not valid JSON */ }
        }
        // Extract scores from session fields as fallback
        if (!session.debrief && session.technical_depth_score != null) {
          setHistoricalDebrief({
            key_insights: [],
            strong_moments: [],
            knowledge_gaps: [],
            scores: {
              technical_depth: session.technical_depth_score ?? 0,
              communication: session.communication_score ?? 0,
              debate_resilience: session.debate_resilience_score ?? 0,
              ai_native: session.ai_native_score ?? 0,
            },
            overall_comment: 'Historical session.',
          })
          setHistoricalXp(session.xp_earned)
        }
      })
      .catch(() => { /* session not found */ })
      .finally(() => setLoading(false))
  }, [routerSessionId, storeDebrief])

  // Use store data for current session, historical data for past sessions
  const debrief = storeDebrief ?? historicalDebrief
  const xpEarned = storeDebrief ? storeXp : historicalXp
  const topic = storeDebrief ? storeTopic : historicalTopic

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

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-[var(--text-dim)]">Loading session...</div>
      </div>
    )
  }

  if (!debrief && !loading) {
    return (
      <div className="flex flex-col items-center justify-center h-full gap-4">
        <div className="text-[var(--text-dim)]">No debrief data available.</div>
        <button onClick={() => navigate('/dashboard')} className="bg-brand text-white px-6 py-2 rounded-lg text-sm">
          Back to Dashboard
        </button>
      </div>
    )
  }

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
