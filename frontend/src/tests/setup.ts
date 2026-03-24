import '@testing-library/jest-dom'

// Mock window.electronAPI
Object.defineProperty(window, 'electronAPI', {
  value: undefined,
  writable: true,
})

// Mock livekit-client to avoid WebRTC in tests
vi.mock('livekit-client', () => ({
  Room: vi.fn().mockImplementation(() => ({
    connect: vi.fn().mockResolvedValue(undefined),
    disconnect: vi.fn(),
    on: vi.fn(),
    localParticipant: {
      setMicrophoneEnabled: vi.fn(),
      publishData: vi.fn(),
    },
  })),
  RoomEvent: {
    DataReceived: 'dataReceived',
  },
}))

// Mock fetch for API calls
globalThis.fetch = vi.fn().mockResolvedValue({
  ok: true,
  json: vi.fn().mockResolvedValue({}),
  status: 200,
}) as unknown as typeof fetch
