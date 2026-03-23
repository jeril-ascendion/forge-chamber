interface XPBarProps {
  current: number
  label?: string
}

export default function XPBar({ current, label }: XPBarProps) {
  const level = Math.floor(current / 500) + 1
  const levelXp = current % 500
  const pct = Math.min((levelXp / 500) * 100, 100)

  return (
    <div>
      {label && <div className="text-xs text-[var(--text-dim)] mb-1">{label}</div>}
      <div className="flex items-center gap-3">
        <div className="text-sm font-semibold text-brand">Lvl {level}</div>
        <div className="flex-1 h-2 bg-[var(--bg-elevated)] rounded-full overflow-hidden">
          <div
            className="h-full bg-brand rounded-full transition-all duration-700"
            style={{ width: `${pct}%` }}
          />
        </div>
        <div className="text-xs text-[var(--text-dim)]">{current} XP</div>
      </div>
    </div>
  )
}
