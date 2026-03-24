import { render, screen } from '@testing-library/react'
import SkillRadar from '../../components/SkillRadar'

describe('SkillRadar', () => {
  const scores = {
    technical_depth: 4.0,
    communication: 3.5,
    debate_resilience: 2.0,
    ai_native: 3.0,
  }

  it('renders an SVG element', () => {
    const { container } = render(<SkillRadar scores={scores} />)
    const svg = container.querySelector('svg')
    expect(svg).toBeInTheDocument()
  })

  it('renders all 4 axis labels', () => {
    render(<SkillRadar scores={scores} />)
    expect(screen.getByText('Technical Depth')).toBeInTheDocument()
    expect(screen.getByText('Communication')).toBeInTheDocument()
    expect(screen.getByText('Debate Resilience')).toBeInTheDocument()
    expect(screen.getByText('AI-Native')).toBeInTheDocument()
  })

  it('renders score polygon', () => {
    const { container } = render(<SkillRadar scores={scores} />)
    const polygons = container.querySelectorAll('polygon')
    // Grid polygons (5 levels) + score polygon = 6
    expect(polygons.length).toBeGreaterThanOrEqual(6)
  })

  it('renders score dots', () => {
    const { container } = render(<SkillRadar scores={scores} />)
    const circles = container.querySelectorAll('circle')
    expect(circles.length).toBe(4) // one per axis
  })
})
