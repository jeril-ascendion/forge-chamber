import { useEffect, useState } from 'react'
import { useAppStore } from '../store/app'
import { updateProfile } from '../lib/api'
import { usePlatform } from '../hooks/usePlatform'
import { ROLE_TRACKS, API_KEY_FIELDS } from '../lib/constants'

export default function Settings() {
  const { engineerName, roleTrack, skillLevel, setEngineer } = useAppStore()
  const { saveApiKeys, getApiKeys } = usePlatform()

  const [name, setName] = useState(engineerName)
  const [role, setRole] = useState(roleTrack)
  const [level, setLevel] = useState(skillLevel)
  const [keys, setKeys] = useState<Record<string, string>>({})
  const [saved, setSaved] = useState(false)

  useEffect(() => {
    getApiKeys().then(setKeys).catch(() => {})
  }, [])

  async function handleSaveProfile() {
    try {
      const profile = await updateProfile({ name, role_track: role, skill_level: level })
      setEngineer(profile)
      setSaved(true)
      setTimeout(() => setSaved(false), 2000)
    } catch { /* ignore */ }
  }

  async function handleSaveKeys() {
    await saveApiKeys(keys)
    setSaved(true)
    setTimeout(() => setSaved(false), 2000)
  }

  return (
    <div className="h-full overflow-y-auto p-6 md:p-8">
      <div className="max-w-lg mx-auto space-y-8">
        <h1 className="text-2xl font-bold">Settings</h1>

        {saved && (
          <div className="bg-green-900/30 text-green-400 px-4 py-2 rounded text-sm">Saved!</div>
        )}

        {/* Profile */}
        <section>
          <h2 className="text-lg font-semibold mb-3">Profile</h2>
          <div className="space-y-3">
            <div>
              <label className="block text-xs text-[var(--text-dim)] mb-1">Name</label>
              <input
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="w-full bg-[var(--bg-card)] border border-[var(--border-dark)] rounded-lg px-4 py-2 focus:outline-none focus:border-brand"
              />
            </div>
            <div>
              <label className="block text-xs text-[var(--text-dim)] mb-1">Role Track</label>
              <select
                value={role}
                onChange={(e) => setRole(e.target.value)}
                className="w-full bg-[var(--bg-card)] border border-[var(--border-dark)] rounded-lg px-4 py-2 focus:outline-none focus:border-brand"
              >
                {ROLE_TRACKS.map((r) => (
                  <option key={r} value={r}>{r}</option>
                ))}
              </select>
            </div>
            <div className="flex gap-4">
              {(['junior', 'mid', 'senior'] as const).map((l) => (
                <label key={l} className="flex items-center gap-2 text-sm cursor-pointer">
                  <input type="radio" checked={level === l} onChange={() => setLevel(l)} className="accent-brand" />
                  <span className="capitalize">{l}</span>
                </label>
              ))}
            </div>
            <button onClick={handleSaveProfile} className="bg-brand text-white px-6 py-2 rounded-lg text-sm">
              Save Profile
            </button>
          </div>
        </section>

        {/* API Keys */}
        <section>
          <h2 className="text-lg font-semibold mb-3">API Keys</h2>
          <div className="space-y-3">
            {API_KEY_FIELDS.map((field) => (
              <div key={field.key}>
                <label className="block text-xs text-[var(--text-dim)] mb-1">{field.label}</label>
                <input
                  type="password"
                  value={keys[field.key] ?? ''}
                  onChange={(e) => setKeys((p) => ({ ...p, [field.key]: e.target.value }))}
                  className="w-full bg-[var(--bg-card)] border border-[var(--border-dark)] rounded-lg px-4 py-2 text-sm focus:outline-none focus:border-brand"
                />
              </div>
            ))}
            <button onClick={handleSaveKeys} className="bg-brand text-white px-6 py-2 rounded-lg text-sm">
              Update Keys
            </button>
          </div>
        </section>

        {/* About */}
        <section className="text-sm text-[var(--text-dim)]">
          <h2 className="text-lg font-semibold mb-2 text-[var(--text)]">About</h2>
          <p>Forge Chamber v1.0.0</p>
          <p>Where engineers get tested</p>
          <p className="mt-1">Built by Ascendion Digital Services</p>
        </section>
      </div>
    </div>
  )
}
