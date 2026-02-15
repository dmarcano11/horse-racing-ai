import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom'
import { AnimatePresence } from 'framer-motion'
import Layout from './components/layout/Layout'
import LandingPage from './pages/LandingPage'
import Dashboard from './pages/Dashboard'
import RaceCardPage from './pages/RaceCardPage'
import ResultsPage from './pages/ResultsPage'
import ChatPage from './pages/ChatPage'

function AnimatedRoutes() {
  const location = useLocation()
  
  return (
    <AnimatePresence mode="wait">
      <Routes location={location} key={location.pathname}>
        {/* Landing page - no layout wrapper */}
        <Route path="/" element={<LandingPage />} />
        
        {/* App routes with layout */}
        <Route element={<Layout />}>
          <Route path="/dashboard" element={<Navigate to="/races" replace />} />
          <Route path="/races" element={<Dashboard />} />
          <Route path="/races/:raceId" element={<RaceCardPage />} />
          <Route path="/results" element={<ResultsPage />} />
          <Route path="/chat" element={<ChatPage />} />
        </Route>
      </Routes>
    </AnimatePresence>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <AnimatedRoutes />
    </BrowserRouter>
  )
}