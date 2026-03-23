import { useState, useCallback } from 'react'

export function useVoice() {
  const [isMicActive, setIsMicActive] = useState(false)
  const [stream, setStream] = useState<MediaStream | null>(null)

  const startMic = useCallback(async () => {
    try {
      const s = await navigator.mediaDevices.getUserMedia({ audio: true })
      setStream(s)
      setIsMicActive(true)
      return s
    } catch {
      setIsMicActive(false)
      return null
    }
  }, [])

  const stopMic = useCallback(() => {
    if (stream) {
      stream.getTracks().forEach((t) => t.stop())
      setStream(null)
    }
    setIsMicActive(false)
  }, [stream])

  return { isMicActive, startMic, stopMic }
}
