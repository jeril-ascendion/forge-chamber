import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAppStore } from '../store/app'
import {
  getProgressSummary,
  getProgressSessions,
  type SkillScores,
  type SessionProgress,
  type ProgressSummary,
} from '../lib/api'
import SkillRadar from '../components/SkillRadar'
import XPBar from '../components/XPBar'

export default function Progress() {
  const navigate = useNavigate()
  const { engineerName, roleTrack } = useAppStore()
  const [summary, setSummary] = useState<ProgressSummary | null>(null)
  const [sessions, setSessions] = useState<SessionProgress[]>([])

  useEffect(() => {
    getProgressSummary().then(setSummary).catch(() => {})
    getProgressSessions().then(setSessions).catch(() => {})
  }, [])

  const skills = summary?.skills ?? { technical_depth: 0, communication: 0, debate_resilience: 0, ai_native: 0 }
  const totalXp = summary?.total_xp ?? 0
  const totalSessions = summary?.total_sessions ?? 0
  const streak = summary?.current_streak ?? 0
  const badges = summary?.badges ?? []

  const domains = [
    { key: 'technical_depth', label: 'Technical Depth', color: '#E8533A' },
    { key: 'communication', label: 'Communication', color: '#2B5EA7' },
    { key: 'debate_resilience', label: 'Debate Resilience', color: '#1D9E75' },
    { key: 'ai_native', label: 'AI-Native', color: '#7F77DD' },
  ]

  return (
    <div className="h-full overflow-y-auto p-6 md:p-8">
      <div className="max-w-3xl mx-auto">
        {/* Profile header */}
        <div className="flex items-center gap-4 mb-6">
          <div className="w-14 h-14 rounded-full bg-brand/20 text-brand flex items-center justify-center text-xl font-bold">
            {engineerName.split(' ').map((w) => w[0]).join('').slice(0, 2).toUpperCase()}
          </div>
          <div className="flex-1">
            <h1 className="text-xl font-bold">{engineerName}</h1>
            <div className="flex gap-3 text-sm text-[var(--text-dim)]">
              <span>{roleTrack}</span>
              <span>-</span>
              <span>{totalSessions} sessions</span>
            </div>
          </div>
          {streak > 1 && (
            <div className="bg-accent/20 text-accent px-3 py-1.5 rounded-lg text-sm font-semibold flex items-center gap-1">
              <span>🔥</span> {streak}-day streak
            </div>
          )}
        </div>

        <XPBar current={totalXp} label="Experience" />

        {/* Badges */}
        {badges.length > 0 && (
          <div className="mt-6">
            <h2 className="text-sm font-semibold text-[var(--text-dim)] uppercase tracking-wider mb-2">Badges</h2>
            <div className="flex flex-wrap gap-2">
              {badges.map((b) => (
                <div
                  key={b.key}
                  className="bg-[var(--bg-card)] border border-[var(--border-dark)] rounded-lg px-3 py-2 text-sm flex items-center gap-2"
                  title={b.description}
                >
                  <span>{b.icon}</span>
                  <span>{b.label}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-8">
          <SkillRadar scores={skills} />

          <div className="space-y-3">
            {domains.map((d) => (
              <div key={d.key}>
                <div className="flex justify-between text-sm mb-1">
                  <span>{d.label}</span>
                  <span className="font-semibold">{(skills[d.key as keyof SkillScores] ?? 0).toFixed(1)} / 5.0</span>
                </div>
                <div className="h-2 bg-[var(--bg-elevated)] rounded-full overflow-hidden">
                  <div
                    className="h-full rounded-full transition-all duration-500"
                    style={{
                      width: `${((skills[d.key as keyof SkillScores] ?? 0) / 5) * 100}%`,
                      backgroundColor: d.color,
                    }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Session history */}
        {sessions.length > 0 && (
          <div className="mt-8">
            <h2 className="text-lg font-semibold mb-3">Session History</h2>
            <div className="bg-[var(--bg-card)] border border-[var(--border-dark)] rounded-xl overflow-hidden">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-[var(--border-dark)] text-[var(--text-dim)] text-xs">
                    <th className="text-left p-3">Date</th>
                    <th className="text-left p-3">Topic</th>
                    <th className="text-right p-3">Duration</th>
                    <th className="text-right p-3">XP</th>
                  </tr>
                </thead>
                <tbody>
                  {sessions.map((s) => (
                    <tr
                      key={s.session_id || s.date}
                      className="border-b border-[var(--border-dark)] last:border-0 hover:bg-[var(--bg-elevated)] cursor-pointer"
                      onClick={() => navigate('/debrief', { state: { sessionId: s.session_id } })}
                    >
                      <td className="p-3 text-[var(--text-dim)]">{new Date(s.date).toLocaleDateString()}</td>
                      <td className="p-3">{s.topic || 'Session'}</td>
                      <td className="p-3 text-right text-[var(--text-dim)]">
                        {s.duration_seconds ? `${Math.floor(s.duration_seconds / 60)}m` : '-'}
                      </td>
                      <td className="p-3 text-right text-brand font-semibold">+{s.xp}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
