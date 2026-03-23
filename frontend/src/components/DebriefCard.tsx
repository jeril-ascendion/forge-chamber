interface DebriefCardProps {
  title: string
  children: React.ReactNode
}

export default function DebriefCard({ title, children }: DebriefCardProps) {
  return (
    <div className="bg-[var(--bg-card)] border border-[var(--border-dark)] rounded-xl p-5 mb-4">
      <h3 className="text-sm font-semibold text-[var(--text-dim)] uppercase tracking-wider mb-3">{title}</h3>
      {children}
    </div>
  )
}
