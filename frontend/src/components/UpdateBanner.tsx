import { useEffect, useState } from 'react'

export default function UpdateBanner() {
  const [updateReady, setUpdateReady] = useState(false)

  useEffect(() => {
    if (window.electronAPI) {
      window.electronAPI.onUpdateReady(() => setUpdateReady(true))
    }
  }, [])

  if (!updateReady) return null

  return (
    <div className="fixed top-0 left-0 right-0 z-50 bg-brand text-white text-sm text-center py-2 px-4 flex items-center justify-center gap-4">
      <span>A new version of Forge Chamber is available.</span>
      <button
        onClick={() => window.electronAPI?.installUpdate()}
        className="bg-white text-brand px-3 py-1 rounded text-xs font-semibold"
      >
        Restart & Update
      </button>
    </div>
  )
}
