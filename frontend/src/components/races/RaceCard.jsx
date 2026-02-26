import { useNavigate } from 'react-router-dom'

export default function RaceCard({ race }) {
  const navigate = useNavigate()
  const isLive = race.status === 'live'

  return (
    <div
      onClick={() => navigate(`/races/${race.id}`)}
      className="cursor-pointer transition-all duration-250"
      style={{
        background: 'var(--card)',
        border: '1px solid var(--border)',
        borderTop: isLive ? '2px solid var(--live)' : undefined,
        borderRadius: '10px',
        padding: '20px 24px',
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.borderColor = 'var(--border-hi)'
        e.currentTarget.style.background = 'var(--card-hi)'
        e.currentTarget.style.transform = 'translateY(-2px)'
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.borderColor = 'var(--border)'
        e.currentTarget.style.background = 'var(--card)'
        e.currentTarget.style.transform = 'translateY(0)'
      }}
    >
      {/* Race Time */}
      <div className="font-display text-xl mb-2" style={{ color: 'var(--gold)' }}>
        {race.postTime || `Race ${race.raceNumber}`}
      </div>

      {/* Race Name */}
      <div className="font-body font-semibold text-sm mb-1" style={{ color: 'var(--cream)' }}>
        {race.raceName || `Race ${race.raceNumber}`}
      </div>

      {/* Meta Info */}
      <div className="font-mono text-xs mb-4" style={{ color: 'var(--muted)' }}>
        {race.trackName} · {race.distanceValue}{race.distanceUnit} · {race.surface}
      </div>

      {/* Bottom Row */}
      <div
        className="flex items-center justify-between pt-3"
        style={{ borderTop: '1px solid rgba(196,158,66,0.08)' }}
      >
        {/* Purse */}
        <div
          className="font-mono text-sm rounded px-2 py-1"
          style={{
            background: 'rgba(196,158,66,0.08)',
            border: '1px solid var(--border)',
            color: 'var(--gold)'
          }}
        >
          {race.purse ? `$${(race.purse / 1000).toFixed(0)}k` : '—'}
        </div>

        {/* Runners Count */}
        <div className="font-mono text-xs" style={{ color: 'var(--muted)' }}>
          {race.numRunners || 0} runners
        </div>
      </div>
    </div>
  )
}
