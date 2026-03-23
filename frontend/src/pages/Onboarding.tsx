import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { usePlatform } from '../hooks/usePlatform'
import { setupEngineer } from '../lib/api'
import { useAppStore } from '../store/app'
import { ROLE_TRACKS, API_KEY_FIELDS } from '../lib/constants'

export default function Onboarding() {
  const navigate = useNavigate()
  const { saveApiKeys } = usePlatform()
  const setEngineer = useAppStore((s) => s.setEngineer)

  const [name, setName] = useState('')
  const [roleTrack, setRoleTrack] = useState('')
  const [skillLevel, setSkillLevel] = useState('mid')
  const [keys, setKeys] = useState<Record<string, string>>({})
  const [showKeys, setShowKeys] = useState<Record<string, boolean>>({})
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const allFilled = name.trim() && roleTrack && API_KEY_FIELDS.every((f) => keys[f.key]?.trim())

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!allFilled) return
    setLoading(true)
    setError('')
    try {
      await saveApiKeys(keys)
      const profile = await setupEngineer({ name: name.trim(), role_track: roleTrack, skill_level: skillLevel })
      setEngineer(profile)
      navigate('/dashboard')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Setup failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex h-full">
      {/* Left brand panel */}
      <div className="hidden md:flex w-[420px] bg-brand flex-col justify-center px-12 text-white">
        <h1 className="text-4xl font-bold mb-2">Forge Chamber</h1>
        <p className="text-white/70 text-lg mb-8">Where engineers get tested</p>
        <ul className="space-y-4 text-white/80 text-sm">
          <li className="flex gap-3">
            <span className="text-accent text-lg">◉</span>
            <span>Debate AI engineering mentors in real-time voice sessions</span>
          </li>
          <li className="flex gap-3">
            <span className="text-accent text-lg">◈</span>
            <span>Track your skills across technical depth, communication, and more</span>
          </li>
          <li className="flex gap-3">
            <span className="text-accent text-lg">⚡</span>
            <span>Earn XP and level up through challenging technical discussions</span>
          </li>
        </ul>
      </div>

      {/* Right form */}
      <div className="flex-1 overflow-y-auto p-8 md:p-12">
        <form onSubmit={handleSubmit} className="max-w-lg mx-auto space-y-6">
          <div>
            <h2 className="text-2xl font-bold mb-1">Set up your profile</h2>
            <p className="text-[var(--text-dim)] text-sm">Configure your engineer profile and API keys to get started.</p>
          </div>

          {error && <div className="bg-accent/20 text-accent px-4 py-2 rounded text-sm">{error}</div>}

          <div>
            <label className="block text-sm text-[var(--text-dim)] mb-1">Name</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Your full name"
              className="w-full bg-[var(--bg-card)] border border-[var(--border-dark)] rounded-lg px-4 py-2.5 text-[var(--text)] focus:outline-none focus:border-brand"
            />
          </div>

          <div>
            <label className="block text-sm text-[var(--text-dim)] mb-1">Role Track</label>
            <select
              value={roleTrack}
              onChange={(e) => setRoleTrack(e.target.value)}
              className="w-full bg-[var(--bg-card)] border border-[var(--border-dark)] rounded-lg px-4 py-2.5 text-[var(--text)] focus:outline-none focus:border-brand"
            >
              <option value="">Select your role...</option>
              {ROLE_TRACKS.map((r) => (
                <option key={r} value={r}>{r}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm text-[var(--text-dim)] mb-2">Skill Level</label>
            <div className="flex gap-4">
              {(['junior', 'mid', 'senior'] as const).map((level) => (
                <label key={level} className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="radio"
                    name="skill"
                    value={level}
                    checked={skillLevel === level}
                    onChange={() => setSkillLevel(level)}
                    className="accent-brand"
                  />
                  <span className="capitalize text-sm">{level}</span>
                </label>
              ))}
            </div>
          </div>

          <div className="border-t border-[var(--border-dark)] pt-4">
            <h3 className="text-lg font-semibold mb-3">API Keys</h3>
            <div className="space-y-3">
              {API_KEY_FIELDS.map((field) => (
                <div key={field.key}>
                  <label className="block text-xs text-[var(--text-dim)] mb-1">{field.label}</label>
                  <div className="relative">
                    <input
                      type={showKeys[field.key] ? 'text' : 'password'}
                      value={keys[field.key] ?? ''}
                      onChange={(e) => setKeys((prev) => ({ ...prev, [field.key]: e.target.value }))}
                      placeholder={field.placeholder}
                      className="w-full bg-[var(--bg-card)] border border-[var(--border-dark)] rounded-lg px-4 py-2 text-sm text-[var(--text)] focus:outline-none focus:border-brand pr-12"
                    />
                    <button
                      type="button"
                      onClick={() => setShowKeys((prev) => ({ ...prev, [field.key]: !prev[field.key] }))}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-[var(--text-dim)]"
                    >
                      {showKeys[field.key] ? 'Hide' : 'Show'}
                    </button>
                  </div>
                </div>
              ))}
            </div>
            <p className="text-xs text-[var(--text-dim)] mt-2">Keys stored in system keychain, never in plaintext.</p>
          </div>

          <button
            type="submit"
            disabled={!allFilled || loading}
            className="w-full bg-accent hover:bg-accent/90 disabled:opacity-40 disabled:cursor-not-allowed text-white font-semibold py-3 rounded-lg transition-colors"
          >
            {loading ? 'Setting up...' : 'Enter the Chamber'}
          </button>
        </form>
      </div>
    </div>
  )
}
