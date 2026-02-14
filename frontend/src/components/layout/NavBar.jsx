import { NavLink } from 'react-router-dom'
import { format } from 'date-fns'

export default function Navbar() {
  return (
    <nav className="bg-slate-800 border-b border-slate-700">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex items-center justify-between h-16">

          {/* Logo */}
          <div className="flex items-center gap-3">
            <span className="text-2xl">🏇</span>
            <div>
              <div className="font-bold text-white tracking-tight">
                Horse Racing AI
              </div>
              <div className="text-xs text-slate-400">
                ML-Powered Predictions
              </div>
            </div>
          </div>

          {/* Nav Links */}
          <div className="flex items-center gap-1">
            <NavLink
              to="/dashboard"
              className={({ isActive }) =>
                `px-4 py-2 rounded-lg text-sm font-medium transition-colors ${isActive
                  ? 'bg-blue-600 text-white'
                  : 'text-slate-400 hover:text-white hover:bg-slate-700'
                }`
              }
            >
              Dashboard
            </NavLink>
            <NavLink
              to="/chat"
              className={({ isActive }) =>
                `px-4 py-2 rounded-lg text-sm font-medium transition-colors ${isActive
                  ? 'bg-blue-600 text-white'
                  : 'text-slate-400 hover:text-white hover:bg-slate-700'
                }`
              }
            >
              AI Chat
            </NavLink>
            <NavLink
              to="/results"
              className={({ isActive }) =>
                `px-4 py-2 rounded-lg text-sm font-medium transition-colors ${isActive
                  ? 'bg-blue-600 text-white'
                  : 'text-slate-400 hover:text-white hover:bg-slate-700'
                }`
              }
            >
              Results
            </NavLink>
          </div>

          {/* Date */}
          <div className="text-sm text-slate-400">
            {format(new Date(), 'EEE, MMM d yyyy')}
          </div>

        </div>
      </div>
    </nav>
  )
}