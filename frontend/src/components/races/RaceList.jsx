import { useNavigate } from 'react-router-dom'

export default function RaceList({ races }) {
  const navigate = useNavigate()

  return (
    <div style={{ background: 'var(--card)', border: '1px solid var(--border)', borderRadius: '12px', overflow: 'hidden' }}>
      {/* Column Headers */}
      <div
        className="grid gap-4 px-6 py-3"
        style={{
          gridTemplateColumns: '60px 1fr 80px 90px 90px 90px 100px',
          borderBottom: '1px solid var(--border)',
          background: 'rgba(0,0,0,0.2)'
        }}
      >
        <div className="font-mono text-[8px] tracking-[0.2em] uppercase" style={{ color: 'var(--muted)' }}>Race</div>
        <div className="font-mono text-[8px] tracking-[0.2em] uppercase" style={{ color: 'var(--muted)' }}>Name</div>
        <div className="font-mono text-[8px] tracking-[0.2em] uppercase" style={{ color: 'var(--muted)' }}>Distance</div>
        <div className="font-mono text-[8px] tracking-[0.2em] uppercase" style={{ color: 'var(--muted)' }}>Surface</div>
        <div className="font-mono text-[8px] tracking-[0.2em] uppercase" style={{ color: 'var(--muted)' }}>Purse</div>
        <div className="font-mono text-[8px] tracking-[0.2em] uppercase" style={{ color: 'var(--muted)' }}>Status</div>
        <div className="font-mono text-[8px] tracking-[0.2em] uppercase" style={{ color: 'var(--muted)' }}></div>
      </div>

      {/* Race Rows */}
      {races.map((race, idx) => {
        const isLive = race.status === 'live'
        return (
          <div
            key={race.id}
            onClick={() => navigate(`/races/${race.id}`)}
            className="grid gap-4 px-6 py-4 items-center cursor-pointer transition-colors"
            style={{
              gridTemplateColumns: '60px 1fr 80px 90px 90px 90px 100px',
              borderBottom: idx !== races.length - 1 ? '1px solid rgba(196,158,66,0.05)' : undefined
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = 'var(--card-hi)'
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = 'transparent'
            }}
          >
            {/* Race Number Circle */}
            <div
              className="flex items-center justify-center rounded-full font-mono text-[12px] font-semibold"
              style={{
                width: '34px',
                height: '34px',
                background: isLive ? 'var(--live-dim)' : 'var(--surface)',
                border: `1px solid ${isLive ? 'var(--live)' : 'var(--border)'}`,
                color: isLive ? 'var(--live)' : 'var(--slate)'
              }}
            >
              {race.raceNumber}
            </div>

            {/* Race Name */}
            <div>
              <div className="text-sm font-medium" style={{ color: 'var(--cream)' }}>
                {race.raceName || `Race ${race.raceNumber}`}
              </div>
              <div className="text-xs mt-0.5" style={{ color: 'var(--muted)' }}>
                {race.raceClass || race.raceType || '—'}
              </div>
            </div>

            {/* Distance */}
            <div className="text-sm font-mono" style={{ color: 'var(--slate)' }}>
              {race.distanceValue ? `${race.distanceValue}${race.distanceUnit}` : '—'}
            </div>

            {/* Surface */}
            <div className="text-sm font-mono" style={{ color: 'var(--slate)' }}>
              {race.surface || '—'}
            </div>

            {/* Purse */}
            <div className="text-sm font-mono font-medium" style={{ color: 'var(--slate)' }}>
              {race.purse ? `$${(race.purse / 1000).toFixed(0)}k` : '—'}
            </div>

            {/* Status */}
            <div>
              {race.hasResults ? (
                <span className="font-mono text-[8px] text-atb-green">Final</span>
              ) : race.hasFinished ? (
                <span className="font-mono text-[8px] text-atb-blue">Official</span>
              ) : (
                <span className="font-mono text-[8px]" style={{ color: 'var(--slate)' }}>Scheduled</span>
              )}
            </div>

            {/* View Link */}
            <div className="text-right font-mono text-[9px]" style={{ color: 'var(--gold)' }}>
              View →
            </div>
          </div>
        )
      })}
    </div>
  )
}
