interface SkillRadarProps {
  scores: { technical_depth: number; communication: number; debate_resilience: number; ai_native: number }
  size?: number
}

const LABELS = ['Technical Depth', 'Communication', 'Debate Resilience', 'AI-Native']
const MAX = 5

export default function SkillRadar({ scores, size = 240 }: SkillRadarProps) {
  const cx = size / 2
  const cy = size / 2
  const r = size / 2 - 30
  const values = [scores.technical_depth, scores.communication, scores.debate_resilience, scores.ai_native]
  const n = values.length

  function point(i: number, val: number): [number, number] {
    const angle = (Math.PI * 2 * i) / n - Math.PI / 2
    const dist = (val / MAX) * r
    return [cx + Math.cos(angle) * dist, cy + Math.sin(angle) * dist]
  }

  const polygon = values.map((v, i) => point(i, v).join(',')).join(' ')
  const gridLevels = [1, 2, 3, 4, 5]

  return (
    <svg width={size} height={size} className="mx-auto">
      {/* Grid rings */}
      {gridLevels.map((level) => {
        const pts = Array.from({ length: n }, (_, i) => point(i, level).join(',')).join(' ')
        return (
          <polygon
            key={level}
            points={pts}
            fill="none"
            stroke="rgba(255,255,255,0.06)"
            strokeWidth={1}
          />
        )
      })}

      {/* Axes */}
      {Array.from({ length: n }, (_, i) => {
        const [ex, ey] = point(i, MAX)
        return <line key={i} x1={cx} y1={cy} x2={ex} y2={ey} stroke="rgba(255,255,255,0.1)" strokeWidth={1} />
      })}

      {/* Score polygon */}
      <polygon
        points={polygon}
        fill="rgba(43, 94, 167, 0.25)"
        stroke="#2B5EA7"
        strokeWidth={2}
        style={{ transition: 'all 0.5s ease' }}
      />

      {/* Score dots */}
      {values.map((v, i) => {
        const [px, py] = point(i, v)
        return <circle key={i} cx={px} cy={py} r={4} fill="#2B5EA7" />
      })}

      {/* Labels */}
      {LABELS.map((label, i) => {
        const [lx, ly] = point(i, MAX + 0.8)
        return (
          <text
            key={label}
            x={lx}
            y={ly}
            textAnchor="middle"
            dominantBaseline="middle"
            className="fill-[var(--text-dim)]"
            fontSize={10}
          >
            {label}
          </text>
        )
      })}
    </svg>
  )
}
