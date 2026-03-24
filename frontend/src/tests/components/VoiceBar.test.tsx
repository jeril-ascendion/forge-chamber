import { render, screen, fireEvent } from '@testing-library/react'
import VoiceBar from '../../components/VoiceBar'

describe('VoiceBar', () => {
  const defaultProps = {
    onJoin: vi.fn(),
    onLeave: vi.fn(),
    isJoined: false,
    maxTurns: 20,
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders in listen mode with "Join Debate" button', () => {
    render(<VoiceBar {...defaultProps} />)
    expect(screen.getByText('Join Debate')).toBeInTheDocument()
  })

  it('shows "You\'re speaking..." when joined', () => {
    render(<VoiceBar {...defaultProps} isJoined={true} />)
    expect(screen.getByText("You're speaking...")).toBeInTheDocument()
  })

  it('shows turn counter', () => {
    render(<VoiceBar {...defaultProps} />)
    expect(screen.getByText('Turn 0 / 20')).toBeInTheDocument()
  })

  it('calls onJoin when button clicked in listen mode', () => {
    render(<VoiceBar {...defaultProps} />)
    fireEvent.click(screen.getByText('Join Debate'))
    expect(defaultProps.onJoin).toHaveBeenCalledTimes(1)
  })

  it('calls onLeave when button clicked in joined mode', () => {
    render(<VoiceBar {...defaultProps} isJoined={true} />)
    fireEvent.click(screen.getByText("You're speaking..."))
    expect(defaultProps.onLeave).toHaveBeenCalledTimes(1)
  })
})
