import { useCallback, useEffect, useRef } from 'react'
import { Room, RoomEvent } from 'livekit-client'
import { useAppStore } from '../store/app'

export function useRoom() {
  const { livekitToken, livekitUrl, addTurn, setActiveSpeaker, setQuizEvent, setDebrief } = useAppStore()
  const roomRef = useRef<Room | null>(null)

  const handleDataMessage = useCallback((payload: Uint8Array) => {
    try {
      const msg = JSON.parse(new TextDecoder().decode(payload)) as Record<string, unknown>
      const type = msg.type as string

      if (type === 'turn_committed') {
        addTurn({
          speaker_type: msg.speaker_type as string,
          speaker_key: msg.speaker_key as string,
          speaker_name: msg.speaker_name as string,
          speaker_role: (msg.speaker_role as string) || '',
          text: msg.text as string,
          turn_number: msg.turn_number as number,
          is_quiz_event: false,
        })
      } else if (type === 'speaker_change') {
        setActiveSpeaker(msg.agent_key as string)
      } else if (type === 'quiz_event') {
        setQuizEvent({
          question: msg.question as string,
          agent_key: msg.agent_key as string,
          timeout_seconds: (msg.timeout_seconds as number) || 30,
        })
      } else if (type === 'session_complete') {
        const debrief = msg.debrief as Record<string, unknown> | undefined
        const xp = msg.xp as { total: number } | undefined
        if (debrief && xp) {
          setDebrief(debrief as unknown as Parameters<typeof setDebrief>[0], xp.total)
        }
      }
    } catch { /* ignore parse errors */ }
  }, [addTurn, setActiveSpeaker, setQuizEvent, setDebrief])

  useEffect(() => {
    if (!livekitToken || !livekitUrl) return

    const room = new Room()
    roomRef.current = room
    room.on(RoomEvent.DataReceived, handleDataMessage)
    room.connect(livekitUrl, livekitToken).catch(console.error)

    return () => {
      room.disconnect()
      roomRef.current = null
    }
  }, [livekitToken, livekitUrl, handleDataMessage])

  function enableMic() {
    roomRef.current?.localParticipant?.setMicrophoneEnabled(true)
  }

  function disableMic() {
    roomRef.current?.localParticipant?.setMicrophoneEnabled(false)
  }

  return { room: roomRef, enableMic, disableMic }
}
