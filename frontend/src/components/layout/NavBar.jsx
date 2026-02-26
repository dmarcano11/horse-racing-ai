import { NavLink, useLocation } from 'react-router-dom'
import { format } from 'date-fns'
import { useState } from 'react'

export default function NavBar() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const location = useLocation()

  return (
    <nav 
      className="fixed top-0 left-0 right-0 z-50"
      style={{
        height: '64px',
        background: 'rgba(8, 11, 16, 0.78)',
        backdropFilter: 'blur(16px) saturate(180%)',
        WebkitBackdropFilter: 'blur(16px) saturate(180%)',
        borderBottom: '1px solid rgba(196,158,66,0.12)'
      }}
    >
      <div className="max-w-7xl mx-auto px-4 h-full">
        <div className="flex items-center justify-between h-full">

          {/* Logo/Brand */}
          <NavLink to="/" className="flex items-center gap-2 cursor-pointer">
            <div>
              <div className="font-display text-2xl font-bold" style={{ color: 'var(--gold)' }}>
                Across the Board
              </div>
              <div className="font-mono text-[12px] tracking-[0.3em] uppercase" style={{ color: 'var(--muted)' }}>
                AI · Research · Predictions
              </div>
            </div>
          </NavLink>

          {/* Nav Links - Desktop */}
          <div className="hidden md:flex items-center gap-1">
            <NavLink
              to="/chat"
              className="font-mono text-[15px] tracking-[0.15em] uppercase px-5 py-2 rounded transition-all"
              style={({ isActive }) => ({
                color: isActive ? 'var(--gold)' : 'var(--slate)',
                background: isActive ? 'rgba(196,158,66,0.08)' : 'transparent',
                border: isActive ? '1px solid var(--border)' : '1px solid transparent'
              })}
            >
              Research
            </NavLink>
            <NavLink
              to="/races"
              className="font-mono text-[15px] tracking-[0.15em] uppercase px-5 py-2 rounded transition-all"
              style={({ isActive }) => ({
                color: isActive ? 'var(--gold)' : 'var(--slate)',
                background: isActive ? 'rgba(196,158,66,0.08)' : 'transparent',
                border: isActive ? '1px solid var(--border)' : '1px solid transparent'
              })}
            >
              Dashboard
            </NavLink>
            <NavLink
              to="/results"
              className="font-mono text-[15px] tracking-[0.15em] uppercase px-5 py-2 rounded transition-all"
              style={({ isActive }) => ({
                color: isActive ? 'var(--gold)' : 'var(--slate)',
                background: isActive ? 'rgba(196,158,66,0.08)' : 'transparent',
                border: isActive ? '1px solid var(--border)' : '1px solid transparent'
              })}
            >
              Results
            </NavLink>
          </div>

          {/* Right Side */}
          <div className="hidden md:flex items-center gap-3">
            {/* Live Indicator */}
            <div 
              className="w-2 h-2 rounded-full pulse"
              style={{ 
                background: 'var(--live)',
                boxShadow: '0 0 6px var(--live)'
              }}
            />
            
            {/* Current Date */}
            <div className="font-mono text-[15px]" style={{ color: 'var(--muted)' }}>
              {format(new Date(), 'EEE, MMM d yyyy')}
            </div>
          </div>

          {/* Mobile Menu Button */}
          <button
            className="md:hidden font-mono text-sm"
            style={{ color: 'var(--gold)' }}
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          >
            ☰
          </button>

        </div>
      </div>

      {/* Mobile Menu Overlay */}
      {mobileMenuOpen && (
        <div 
          className="md:hidden absolute top-16 left-0 right-0 p-4 flex flex-col gap-2"
          style={{
            background: 'rgba(8, 11, 16, 0.95)',
            backdropFilter: 'blur(16px)',
            borderBottom: '1px solid rgba(196,158,66,0.12)'
          }}
        >
          <NavLink
            to="/chat"
            className="font-mono text-xs tracking-[0.15em] uppercase px-4 py-3 rounded"
            style={{
              color: location.pathname === '/chat' ? 'var(--gold)' : 'var(--slate)',
              background: location.pathname === '/chat' ? 'rgba(196,158,66,0.08)' : 'transparent',
              border: `1px solid ${location.pathname === '/chat' ? 'var(--border)' : 'transparent'}`
            }}
            onClick={() => setMobileMenuOpen(false)}
          >
            Research
          </NavLink>
          <NavLink
            to="/races"
            className="font-mono text-xs tracking-[0.15em] uppercase px-4 py-3 rounded"
            style={{
              color: location.pathname === '/races' ? 'var(--gold)' : 'var(--slate)',
              background: location.pathname === '/races' ? 'rgba(196,158,66,0.08)' : 'transparent',
              border: `1px solid ${location.pathname === '/races' ? 'var(--border)' : 'transparent'}`
            }}
            onClick={() => setMobileMenuOpen(false)}
          >
            Dashboard
          </NavLink>
          <NavLink
            to="/results"
            className="font-mono text-xs tracking-[0.15em] uppercase px-4 py-3 rounded"
            style={{
              color: location.pathname === '/results' ? 'var(--gold)' : 'var(--slate)',
              background: location.pathname === '/results' ? 'rgba(196,158,66,0.08)' : 'transparent',
              border: `1px solid ${location.pathname === '/results' ? 'var(--border)' : 'transparent'}`
            }}
            onClick={() => setMobileMenuOpen(false)}
          >
            Results
          </NavLink>
        </div>
      )}
    </nav>
  )
}