import { useLocation, useNavigate } from 'react-router-dom'
import { useAppStore } from '../store/app'

const NAV_ITEMS = [
  { path: '/dashboard', label: 'Home', icon: '⌂' },
  { path: '/room/setup', label: 'Room', icon: '◉' },
  { path: '/progress', label: 'Progress', icon: '◈' },
  { path: '/settings', label: 'Settings', icon: '⚙' },
]

export default function NavBar() {
  const location = useLocation()
  const navigate = useNavigate()
  const name = useAppStore((s) => s.engineerName)
  const initials = name
    .split(' ')
    .map((w) => w[0])
    .join('')
    .toUpperCase()
    .slice(0, 2)

  return (
    <>
      {/* Desktop sidebar */}
      <nav className="nav-sidebar bg-[var(--bg-card)] border-r border-[var(--border-dark)] flex flex-col items-center py-4 gap-2">
        <div className="text-accent font-bold text-lg mb-4">FC</div>
        {NAV_ITEMS.map((item) => (
          <button
            key={item.path}
            onClick={() => navigate(item.path)}
            className={`w-10 h-10 rounded-lg flex items-center justify-center text-lg transition-colors ${
              location.pathname === item.path
                ? 'bg-brand text-white'
                : 'text-[var(--text-dim)] hover:bg-[var(--bg-elevated)]'
            }`}
            title={item.label}
          >
            {item.icon}
          </button>
        ))}
        <div className="mt-auto">
          <div className="w-10 h-10 rounded-full bg-brand/20 text-brand flex items-center justify-center text-sm font-semibold">
            {initials || '?'}
          </div>
        </div>
      </nav>

      {/* Mobile bottom nav */}
      <nav className="nav-bottom bg-[var(--bg-card)] border-t border-[var(--border-dark)] items-center justify-around z-50">
        {NAV_ITEMS.map((item) => (
          <button
            key={item.path}
            onClick={() => navigate(item.path)}
            className={`flex flex-col items-center gap-1 text-xs ${
              location.pathname === item.path ? 'text-brand' : 'text-[var(--text-dim)]'
            }`}
          >
            <span className="text-lg">{item.icon}</span>
            <span>{item.label}</span>
          </button>
        ))}
      </nav>
    </>
  )
}
