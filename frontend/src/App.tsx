import { useEffect, useState } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { usePlatform } from './hooks/usePlatform'
import { getProfile } from './lib/api'
import { useAppStore } from './store/app'
import NavBar from './components/NavBar'
import Onboarding from './pages/Onboarding'
import Dashboard from './pages/Dashboard'
import RoomSetup from './pages/RoomSetup'
import RoomActive from './pages/RoomActive'
import Debrief from './pages/Debrief'
import Progress from './pages/Progress'
import Settings from './pages/Settings'

export default function App() {
  const { hasApiKeys } = usePlatform()
  const setEngineer = useAppStore((s) => s.setEngineer)
  const [ready, setReady] = useState(false)
  const [hasKeys, setHasKeys] = useState(false)

  useEffect(() => {
    async function init() {
      const keys = await hasApiKeys()
      setHasKeys(keys)
      if (keys) {
        try {
          const profile = await getProfile()
          setEngineer(profile)
        } catch {
          // No profile yet — will redirect to onboarding
          setHasKeys(false)
        }
      }
      setReady(true)
    }
    init()
  }, [hasApiKeys, setEngineer])

  if (!ready) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-text-dim text-lg">Loading...</div>
      </div>
    )
  }

  return (
    <div className="flex h-screen">
      {hasKeys && <NavBar />}
      <main className="flex-1 overflow-hidden">
        <Routes>
          <Route path="/onboarding" element={<Onboarding />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/room/setup" element={<RoomSetup />} />
          <Route path="/room/active" element={<RoomActive />} />
          <Route path="/debrief" element={<Debrief />} />
          <Route path="/progress" element={<Progress />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="*" element={<Navigate to={hasKeys ? '/dashboard' : '/onboarding'} replace />} />
        </Routes>
      </main>
    </div>
  )
}
