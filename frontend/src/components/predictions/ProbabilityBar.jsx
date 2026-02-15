import { useState, useEffect } from 'react'

export default function ProbabilityBar({ probability }) {
  const [width, setWidth] = useState(0)
  
  const pct = probability ? (probability * 100).toFixed(1) : '0'
  const targetWidth = probability ? Math.min((probability * 100) / 30 * 100, 100) : 0 // Scale to 30% max

  // Animate bar on mount
  useEffect(() => {
    const timer = setTimeout(() => {
      setWidth(targetWidth)
    }, 50)
    return () => clearTimeout(timer)
  }, [targetWidth])

  if (!probability) return <span className="text-slate-500 text-sm font-mono">—</span>

  return (
    <div className="flex items-center gap-2">
      <div 
        className="flex-1 h-1.5 rounded-full overflow-hidden" 
        style={{ background: 'rgba(255,255,255,0.05)' }}
      >
        <div
          className="h-full rounded-full transition-all duration-700"
          style={{
            width: `${width}%`,
            background: 'linear-gradient(90deg, var(--blue), var(--gold))'
          }}
        />
      </div>
      <span 
        className="font-mono text-[11px] min-w-[38px] text-right"
        style={{ color: 'var(--gold)' }}
      >
        {pct}%
      </span>
    </div>
  )
}