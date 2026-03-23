import { useAppStore } from '../store/app'

export function useTranscript() {
  const transcript = useAppStore((s) => s.transcript)
  const addTurn = useAppStore((s) => s.addTurn)
  const activeSpeaker = useAppStore((s) => s.activeSpeaker)

  function addHumanTurn(text: string) {
    addTurn({
      speaker_type: 'human',
      speaker_key: 'human',
      speaker_name: 'You',
      speaker_role: 'Student',
      text,
      turn_number: transcript.length,
      is_quiz_event: false,
    })
  }

  return { transcript, activeSpeaker, addTurn, addHumanTurn }
}
