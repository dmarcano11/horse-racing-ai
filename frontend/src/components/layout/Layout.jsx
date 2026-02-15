import { Outlet } from 'react-router-dom'
import NavBar from './NavBar'

export default function Layout() {
  return (
    <div className="min-h-screen" style={{ background: 'var(--deep)', color: 'var(--cream)' }}>
      <NavBar />
      <main className="max-w-7xl mx-auto px-4 py-6" style={{ paddingTop: '80px' }}>
        <Outlet />
      </main>
    </div>
  )
}