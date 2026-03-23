export const AGENT_KEYS = ['sre', 'sys_arch', 'cloud_eng', 'java_dev', 'ui_dev'] as const
export type AgentKey = (typeof AGENT_KEYS)[number]

export interface AgentDef {
  key: AgentKey
  name: string
  role: string
  color: string
  mandate: string
}

export const AGENTS: Record<AgentKey, AgentDef> = {
  sre: { key: 'sre', name: 'Alex', role: 'SRE', color: '#E8533A', mandate: 'Reliability, SLOs, blast radius, runbooks' },
  sys_arch: { key: 'sys_arch', name: 'Maya', role: 'Systems Architect', color: '#2B5EA7', mandate: 'System design, trade-offs, scalability' },
  cloud_eng: { key: 'cloud_eng', name: 'Ravi', role: 'Cloud Engineer', color: '#1D9E75', mandate: 'AWS/IaC, costs, networking, ops' },
  java_dev: { key: 'java_dev', name: 'Sam', role: 'Senior Java Dev', color: '#BA7517', mandate: 'JVM, transactions, Spring Boot, type safety' },
  ui_dev: { key: 'ui_dev', name: 'Jordan', role: 'Senior UI Dev', color: '#7F77DD', mandate: 'Components, state, performance, accessibility' },
}

export const ROLE_TRACKS = [
  'UI Developer',
  'Java Developer',
  'Cloud Engineer',
  'Solutions Architect',
  'SRE',
] as const

export const SKILL_LEVELS = ['junior', 'mid', 'senior'] as const

export const PRESET_TOPICS = [
  'Microservices vs Monolith for a fintech startup',
  'Event-driven architecture for real-time analytics',
  'Migrating a legacy system to cloud-native',
  'API gateway design for multi-tenant SaaS',
  'CI/CD pipeline for a regulated healthcare app',
  'Scaling a social media feed to 10M users',
]

export const API_KEY_FIELDS = [
  { key: 'LIVEKIT_URL', label: 'LiveKit URL', placeholder: 'wss://your-project.livekit.cloud' },
  { key: 'LIVEKIT_API_KEY', label: 'LiveKit API Key', placeholder: 'API...' },
  { key: 'LIVEKIT_API_SECRET', label: 'LiveKit API Secret', placeholder: 'secret...' },
  { key: 'GROQ_API_KEY', label: 'Groq API Key', placeholder: 'gsk_...' },
  { key: 'DEEPGRAM_API_KEY', label: 'Deepgram API Key', placeholder: 'dg_...' },
  { key: 'CARTESIA_API_KEY', label: 'Cartesia API Key', placeholder: 'sk_...' },
] as const
