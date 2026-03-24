import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import ContextDrop from '../../components/ContextDrop'

// Mock the API module
vi.mock('../../lib/api', () => ({
  ingestUrl: vi.fn().mockResolvedValue({ status: 'ingested', chunks: 5, title: 'Test' }),
  ingestFile: vi.fn().mockResolvedValue({ status: 'ingested', chunks: 3, title: 'File' }),
  getSources: vi.fn().mockResolvedValue([]),
  deleteSource: vi.fn().mockResolvedValue({ status: 'deleted' }),
}))

describe('ContextDrop', () => {
  it('renders URL input', () => {
    render(<ContextDrop />)
    expect(screen.getByPlaceholderText('Paste a URL...')).toBeInTheDocument()
  })

  it('renders Add button', () => {
    render(<ContextDrop />)
    expect(screen.getByText('Add')).toBeInTheDocument()
  })

  it('renders file upload area', () => {
    render(<ContextDrop />)
    expect(screen.getByText(/Drop files here/)).toBeInTheDocument()
  })

  it('Add button disabled when URL empty', () => {
    render(<ContextDrop />)
    const button = screen.getByText('Add')
    expect(button).toBeDisabled()
  })

  it('URL input accepts text', () => {
    render(<ContextDrop />)
    const input = screen.getByPlaceholderText('Paste a URL...')
    fireEvent.change(input, { target: { value: 'https://example.com' } })
    expect(input).toHaveValue('https://example.com')
  })
})
