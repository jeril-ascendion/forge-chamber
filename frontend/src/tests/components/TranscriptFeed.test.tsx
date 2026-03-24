import { render, screen } from '@testing-library/react'
import { useAppStore } from '../../store/app'

// We need to set store state before rendering
function setTranscript(turns: Parameters<typeof useAppStore.getState>['addTurn'][]) {
  const store = useAppStore.getState()
  store.resetSession()
  for (const turn of turns) {
    store.addTurn(turn as ReturnType<typeof useAppStore.getState>['transcript'][0])
  }
}

// Import after mocking
import TranscriptFeed from '../../components/TranscriptFeed'

describe('TranscriptFeed', () => {
  beforeEach(() => {
    useAppStore.getState().resetSession()
  })

  it('renders empty state with no turns', () => {
    render(<TranscriptFeed />)
    expect(screen.getByText('Waiting for debate to start...')).toBeInTheDocument()
  })

  it('renders agent turn with speaker name', () => {
    setTranscript([{
      speaker_type: 'agent',
      speaker_key: 'sre',
      speaker_name: 'Alex',
      speaker_role: 'SRE',
      text: 'What about your SLO strategy?',
      turn_number: 0,
      is_quiz_event: false,
    }])

    render(<TranscriptFeed />)
    expect(screen.getByText('Alex')).toBeInTheDocument()
    expect(screen.getByText('What about your SLO strategy?')).toBeInTheDocument()
  })

  it('renders human turn with "You" label', () => {
    setTranscript([{
      speaker_type: 'human',
      speaker_key: 'human',
      speaker_name: 'Student',
      speaker_role: 'Engineer',
      text: 'We target 99.9% availability.',
      turn_number: 0,
      is_quiz_event: false,
    }])

    render(<TranscriptFeed />)
    expect(screen.getByText('You')).toBeInTheDocument()
  })

  it('renders quiz event with Quiz label', () => {
    setTranscript([{
      speaker_type: 'system',
      speaker_key: 'sre',
      speaker_name: 'Alex',
      speaker_role: 'quiz',
      text: 'What is a circuit breaker?',
      turn_number: 0,
      is_quiz_event: true,
    }])

    render(<TranscriptFeed />)
    expect(screen.getByText('Quiz')).toBeInTheDocument()
  })
})
