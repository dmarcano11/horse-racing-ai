import { Outlet } from 'react-router-dom'
import Navbar from './Navbar'

export default function Layout() {
  return (
    <div className="min-h-screen" style={{ background: 'var(--deep)', color: 'var(--cream)' }}>
      <Navbar />
      <main className="max-w-7xl mx-auto px-4 py-6" style={{ paddingTop: '80px' }}>
        <Outlet />
      </main>
    </div>
  )
}