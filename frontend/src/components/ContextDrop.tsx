import { useEffect, useState } from 'react'
import { ingestUrl, ingestFile, getSources, deleteSource, type RagSource } from '../lib/api'

export default function ContextDrop() {
  const [url, setUrl] = useState('')
  const [sources, setSources] = useState<RagSource[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    getSources().then(setSources).catch(() => {})
  }, [])

  async function handleAddUrl() {
    if (!url.trim()) return
    setLoading(true)
    setError('')
    try {
      await ingestUrl(url.trim())
      setUrl('')
      setSources(await getSources())
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Ingestion failed')
    } finally {
      setLoading(false)
    }
  }

  async function handleFile(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0]
    if (!file) return
    setLoading(true)
    setError('')
    try {
      await ingestFile(file)
      setSources(await getSources())
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed')
    } finally {
      setLoading(false)
    }
  }

  async function handleDelete(id: string) {
    await deleteSource(id)
    setSources(await getSources())
  }

  return (
    <div className="space-y-3">
      <div className="flex gap-2">
        <input
          type="text"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleAddUrl()}
          placeholder="Paste a URL..."
          className="flex-1 bg-[var(--bg)] border border-[var(--border-dark)] rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-brand"
        />
        <button
          onClick={handleAddUrl}
          disabled={loading || !url.trim()}
          className="px-4 py-2 bg-brand text-white rounded-lg text-sm disabled:opacity-40"
        >
          {loading ? '...' : 'Add'}
        </button>
      </div>

      <label className="block border-2 border-dashed border-[var(--border-dark)] rounded-lg p-4 text-center text-sm text-[var(--text-dim)] cursor-pointer hover:border-brand/40 transition-colors">
        <input type="file" onChange={handleFile} accept=".pdf,.docx,.txt,.md" className="hidden" />
        {loading ? 'Processing...' : 'Drop files here or click to browse (PDF, DOCX, TXT, MD)'}
      </label>

      {error && <div className="text-accent text-xs">{error}</div>}

      {sources.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {sources.map((s) => (
            <div
              key={s.id}
              className="flex items-center gap-2 bg-[var(--bg-elevated)] rounded-full px-3 py-1 text-xs"
            >
              <span className="truncate max-w-[160px]">{s.label}</span>
              <span className="text-[var(--text-dim)]">{s.chunks}ch</span>
              <button onClick={() => handleDelete(s.id)} className="text-accent hover:text-accent/80">
                ×
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
