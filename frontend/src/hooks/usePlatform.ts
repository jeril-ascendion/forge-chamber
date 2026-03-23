interface ElectronAPI {
  pickFiles: () => Promise<string[]>
  readFile: (path: string) => Promise<ArrayBuffer>
  saveApiKeys: (keys: Record<string, string>) => Promise<void>
  getApiKeys: () => Promise<Record<string, string>>
  hasApiKeys: () => Promise<boolean>
  onUpdateReady: (cb: () => void) => void
  installUpdate: () => Promise<void>
  getSidecarPort: () => Promise<number>
  getDataDir: () => Promise<string>
  onSidecarRestarted: (cb: () => void) => void
  onSidecarFailed: (cb: () => void) => void
}

declare global {
  interface Window {
    electronAPI?: ElectronAPI
  }
}

function webFilePicker(): Promise<string[]> {
  return new Promise((resolve) => {
    const input = document.createElement('input')
    input.type = 'file'
    input.multiple = true
    input.accept = '.pdf,.docx,.txt,.md'
    input.onchange = () => {
      const files = Array.from(input.files ?? [])
      resolve(files.map((f) => f.name))
    }
    input.click()
  })
}

export function usePlatform() {
  const isElectron = !!window.electronAPI
  const isWeb = !isElectron

  async function pickFiles(): Promise<string[]> {
    if (isElectron) return window.electronAPI!.pickFiles()
    return webFilePicker()
  }

  async function requestMic(): Promise<MediaStream> {
    return navigator.mediaDevices.getUserMedia({ audio: true })
  }

  async function saveApiKeys(keys: Record<string, string>): Promise<void> {
    if (isElectron) return window.electronAPI!.saveApiKeys(keys)
    Object.entries(keys).forEach(([k, v]) => localStorage.setItem(k, v))
  }

  async function hasApiKeys(): Promise<boolean> {
    if (isElectron) return window.electronAPI!.hasApiKeys()
    return !!localStorage.getItem('GROQ_API_KEY')
  }

  async function getApiKeys(): Promise<Record<string, string>> {
    if (isElectron) return window.electronAPI!.getApiKeys()
    const keys: Record<string, string> = {}
    for (const k of ['LIVEKIT_URL', 'LIVEKIT_API_KEY', 'LIVEKIT_API_SECRET', 'GROQ_API_KEY', 'DEEPGRAM_API_KEY', 'CARTESIA_API_KEY']) {
      keys[k] = localStorage.getItem(k) ?? ''
    }
    return keys
  }

  return { isElectron, isWeb, pickFiles, requestMic, saveApiKeys, hasApiKeys, getApiKeys }
}
