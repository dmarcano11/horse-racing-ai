import { useNavigate } from 'react-router-dom'

export default function FeatureDashPreview() {
  const navigate = useNavigate()

  const races = [
    { num: 1, name: 'Maiden Special Weight', distance: '6F', surface: 'Dirt', purse: '$75k', status: 'Upcoming' },
    { num: 2, name: 'Allowance', distance: '1M', surface: 'Turf', purse: '$85k', status: 'Live' },
    { num: 3, name: 'Claiming', distance: '7F', surface: 'Dirt', purse: '$50k', status: 'Upcoming' },
  ]

  return (
    <div 
      onClick={() => navigate('/races')}
      className="cursor-pointer rounded-2xl overflow-hidden transition-all"
      style={{
        background: 'var(--card)',
        border: '1px solid var(--border)',
      }}
    >
      {/* Track Tabs */}
      <div className="p-4 flex gap-2" style={{ borderBottom: '1px solid var(--border)' }}>
        {['Aqueduct', 'Gulfstream', 'Santa Anita'].map((track, i) => (
          <div
            key={track}
            className="px-3 py-1.5 rounded-full font-mono text-[9px] flex items-center gap-1.5"
            style={{
              background: i === 0 ? 'rgba(196,158,66,0.10)' : 'var(--surface)',
              border: `1px solid ${i === 0 ? 'var(--gold)' : 'var(--border)'}`,
              color: i === 0 ? 'var(--gold)' : 'var(--slate)'
            }}
          >
            {track}
            <span className="px-1.5 py-0.5 rounded-full text-[8px]" style={{
              background: i === 0 ? 'rgba(196,158,66,0.2)' : 'rgba(255,255,255,0.05)',
              color: i === 0 ? 'var(--gold-light)' : 'var(--muted)'
            }}>
              {i === 0 ? '8' : i === 1 ? '9' : '7'}
            </span>
          </div>
        ))}
      </div>

      {/* Race Rows */}
      <div>
        {races.map((race, i) => (
          <div
            key={i}
            className="grid gap-3 px-4 py-3 items-center transition-colors"
            style={{
              gridTemplateColumns: '40px 1fr 60px 70px 60px',
              borderBottom: i !== races.length - 1 ? '1px solid rgba(196,158,66,0.05)' : undefined
            }}
          >
            <div className="w-8 h-8 rounded-full flex items-center justify-center font-mono text-xs font-semibold" style={{
              background: race.status === 'Live' ? 'var(--live-dim)' : 'var(--surface)',
              border: `1px solid ${race.status === 'Live' ? 'var(--live)' : 'var(--border)'}`,
              color: race.status === 'Live' ? 'var(--live)' : 'var(--slate)'
            }}>
              {race.num}
            </div>
            <div>
              <div className="text-xs font-medium" style={{ color: 'var(--cream)' }}>{race.name}</div>
            </div>
            <div className="text-xs font-mono" style={{ color: 'var(--slate)' }}>{race.distance}</div>
            <div className="text-xs font-mono" style={{ color: 'var(--slate)' }}>{race.surface}</div>
            <div className="text-xs font-mono" style={{ color: 'var(--gold)' }}>{race.purse}</div>
          </div>
        ))}
      </div>

      {/* Hover Hint */}
      <div className="px-4 py-2 text-center font-mono text-[9px]" style={{ color: 'var(--gold)', borderTop: '1px solid var(--border)' }}>
        Click to view live races →
      </div>
    </div>
  )
}
