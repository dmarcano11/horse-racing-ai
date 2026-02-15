import { useNavigate } from 'react-router-dom'

export default function FeaturePredPreview() {
  const navigate = useNavigate()

  const runners = [
    { num: 5, name: 'Midnight Thunder', jockey: 'J. Ortiz', prob: 28.4, isTopPick: true },
    { num: 3, name: 'Golden Sunset', jockey: 'I. Ortiz Jr.', prob: 22.1, isTopPick: false },
    { num: 7, name: 'Fast Break', jockey: 'J. Rosario', prob: 18.7, isTopPick: false },
    { num: 1, name: 'Lucky Seven', jockey: 'M. Franco', prob: 15.3, isTopPick: false },
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
      <div className="p-4 space-y-3">
        {runners.map((runner, i) => (
          <div
            key={i}
            className="rounded-lg p-3 grid gap-2 items-center"
            style={{
              gridTemplateColumns: '32px 1fr 140px',
              background: runner.isTopPick ? 'rgba(74,143,232,0.04)' : 'var(--surface)',
              border: `1px solid ${runner.isTopPick ? 'rgba(74,143,232,0.35)' : 'var(--border)'}`,
            }}
          >
            {/* Number */}
            <div className="w-8 h-8 rounded-full flex items-center justify-center font-mono text-xs font-semibold" style={{
              background: runner.isTopPick ? 'var(--blue-dim)' : 'var(--surface)',
              border: `1px solid ${runner.isTopPick ? 'var(--blue)' : 'var(--border)'}`,
              color: runner.isTopPick ? 'var(--blue)' : 'var(--slate)'
            }}>
              {runner.num}
            </div>

            {/* Horse Info */}
            <div>
              <div className="font-display text-sm font-semibold mb-0.5" style={{ color: 'var(--cream)' }}>
                {runner.name}
              </div>
              <div className="font-mono text-[9px]" style={{ color: 'var(--muted)' }}>
                {runner.jockey}
              </div>
              {runner.isTopPick && (
                <div className="inline-flex items-center gap-1 font-mono text-[7px] mt-1 rounded-full px-2 py-0.5" style={{
                  color: 'var(--gold)',
                  background: 'rgba(196,158,66,0.1)',
                  border: '1px solid rgba(196,158,66,0.2)'
                }}>
                  ★ Model Top Pick
                </div>
              )}
            </div>

            {/* Probability */}
            <div>
              <div className="flex items-center gap-2">
                <div className="flex-1 h-1.5 rounded-full overflow-hidden" style={{ background: 'rgba(255,255,255,0.05)' }}>
                  <div className="h-full rounded-full" style={{
                    width: `${(runner.prob / 30) * 100}%`,
                    background: 'linear-gradient(90deg, var(--blue), var(--gold))'
                  }} />
                </div>
                <span className="font-mono text-[10px] min-w-[32px] text-right" style={{ color: 'var(--gold)' }}>
                  {runner.prob}%
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Hover Hint */}
      <div className="px-4 py-2 text-center font-mono text-[9px]" style={{ color: 'var(--gold)', borderTop: '1px solid var(--border)' }}>
        Click to see full predictions →
      </div>
    </div>
  )
}
