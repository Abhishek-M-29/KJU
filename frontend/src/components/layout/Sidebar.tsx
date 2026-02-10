import { NavLink } from 'react-router-dom'
import { LayoutDashboard, Settings, LogOut } from 'lucide-react'
import { cn } from '@/lib/utils'

interface SidebarProps {
  onLogout?: () => void
}

export function Sidebar({ onLogout }: SidebarProps) {
  const navItems = [
    { to: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
    { to: '/settings', icon: Settings, label: 'Settings' },
  ]

  return (
    <aside className="w-64 h-screen fixed left-0 top-0 glass-card rounded-none rounded-r-3xl p-6 flex flex-col">
      {/* Logo */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold gradient-text">Kju</h1>
        <p className="text-xs text-text-muted">Medical Systems</p>
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-2">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              cn(
                'flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200',
                isActive
                  ? 'bg-primary text-white shadow-lg shadow-primary/25'
                  : 'text-text-secondary hover:bg-white/50 hover:text-text-primary'
              )
            }
          >
            <item.icon className="w-5 h-5" />
            <span className="font-medium">{item.label}</span>
          </NavLink>
        ))}
      </nav>

      {/* Logout */}
      <button
        onClick={onLogout}
        className="flex items-center gap-3 px-4 py-3 rounded-xl text-text-secondary hover:bg-risk-critical/10 hover:text-risk-critical transition-all duration-200"
      >
        <LogOut className="w-5 h-5" />
        <span className="font-medium">Logout</span>
      </button>
    </aside>
  )
}
