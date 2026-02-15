import { useNavigate } from 'react-router-dom'

export default function FeatureResultsPreview() {
  const navigate = useNavigate()

  const results = [
    { race: 'Race 5', track: 'Gulfstream', winner: 'Midnight Thunder', modelCorrect: true, modelRank: 1 },
    { race: 'Race 3', track: 'Aqueduct', winner: 'Fast Break', modelCorrect: true, modelRank: 1 },
    { race: 'Race 7', track: 'Santa Anita', winner: 'Golden Sunset', modelCorrect: false, modelRank: 3 },
    { race: 'Race 2', track: 'Gulfstream', winner: 'Lucky Seven', modelCorrect: false, modelRank: 4 },
  ]

  return (
    <div className="grid md:grid-cols-2 gap-4">
      {results.map((result, i) => (
        <div
          key={i}
          onClick={() => navigate('/results')}
          className="cursor-pointer rounded-xl p-4 transition-all"
          style={{
            background: 'var(--card)',
            border: `1px solid ${result.modelCorrect ? 'rgba(60,184,122,0.25)' : 'rgba(224,75,53,0.25)'}`,
          }}
        >
          {/* Banner */}
          <div
            className="rounded-lg px-3 py-2 mb-3 flex items-center gap-2 font-mono text-xs"
            style={{
              background: result.modelCorrect ? 'rgba(60,184,122,0.1)' : 'rgba(224,75,53,0.1)',
              border: `1px solid ${result.modelCorrect ? 'rgba(60,184,122,0.3)' : 'rgba(224,75,53,0.3)'}`,
              color: result.modelCorrect ? 'var(--green)' : 'var(--live)'
            }}
          >
            <span className="text-lg">{result.modelCorrect ? '✓' : '✕'}</span>
            <span>{result.modelCorrect ? 'Model Correct' : 'Model Missed'}</span>
          </div>

          {/* Race Info */}
          <div className="mb-2">
            <div className="font-display text-base font-semibold mb-1" style={{ color: 'var(--cream)' }}>
              {result.race} · {result.track}
            </div>
            <div className="font-mono text-[10px]" style={{ color: 'var(--slate)' }}>
              Winner: {result.winner}
            </div>
          </div>

          {/* Model Rank */}
          <div className="font-mono text-[9px]" style={{ color: 'var(--muted)' }}>
            Model ranked this horse #{result.modelRank}
          </div>
        </div>
      ))}
    </div>
  )
}
