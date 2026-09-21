import { Link, Outlet, useLocation, useNavigate } from 'react-router-dom'
import { LayoutDashboard, LogOut } from 'lucide-react'
import { useAuthStore } from '../store/authStore'

export function AppLayout() {
  const { logout } = useAuthStore()
  const navigate = useNavigate()
  const location = useLocation()

  const isDashboard = location.pathname === '/dashboard'

  return (
    <div className="min-h-screen bg-slate-50">
      <header className="sticky top-0 z-40 flex h-14 items-center justify-between border-b border-slate-200 bg-white/80 px-4 backdrop-blur-sm sm:px-6">
        <Link to="/dashboard" className="flex items-center gap-2.5 text-sm font-semibold text-slate-900">
          <img src="/logo.png" alt="Midnight" className="h-8 w-auto rounded-md" />
          <span className="hidden sm:inline">ATS Resume Builder</span>
        </Link>
        <nav className="flex items-center gap-1 text-sm">
          <Link
            to="/dashboard"
            className={`flex items-center gap-1.5 rounded-lg px-3 py-1.5 font-medium transition-colors ${
              isDashboard ? 'bg-brand-50 text-brand-700' : 'text-slate-500 hover:bg-slate-100 hover:text-slate-800'
            }`}
          >
            <LayoutDashboard size={15} />
            <span className="hidden sm:inline">Dashboard</span>
          </Link>
          <span className="mx-1 h-5 w-px bg-slate-200" />
          <button
            onClick={() => {
              logout()
              navigate('/login')
            }}
            className="flex items-center gap-1.5 rounded-lg px-3 py-1.5 font-medium text-slate-500 transition-colors hover:bg-danger-50 hover:text-danger-600"
          >
            <LogOut size={15} />
            <span className="hidden sm:inline">Log out</span>
          </button>
        </nav>
      </header>
      <Outlet />
    </div>
  )
}
