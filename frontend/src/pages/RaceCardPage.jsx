import { useParams, useNavigate } from 'react-router-dom'
import { useRaceCard } from '../hooks/usePredictions'
import LoadingSpinner from '../components/ui/LoadingSpinner'
import ErrorMessage from '../components/ui/ErrorMessage'
import RunnerRow from '../components/races/RunnerRow'
import ChatPanel from '../components/chat/ChatPanel'

export default function RaceCardPage() {
  const { raceId } = useParams()
  const navigate = useNavigate()
  const { raceCard, loading, error } = useRaceCard(raceId)

  if (loading) return <LoadingSpinner message="Loading race card & predictions..." />
  if (error) return <ErrorMessage message={error} />
  if (!raceCard) return null

  const { race, runners, hasResults, predictionsAvailable } = raceCard

  const formatPurse = (p) => p ? `$${p.toLocaleString()}` : '—'
  const formatDistance = (r) => r.distanceValue
    ? `${r.distanceValue}${r.distanceUnit || 'F'}`
    : '—'

  // Find winner if results available
  const winner = hasResults ? runners.find(r => r.finishPosition === 1) : null
  const modelCorrect = winner?.modelRank === 1

  return (
    <div className="space-y-6">

      {/* Back Button */}
      <button
        onClick={() => navigate(-1)}
        className="font-mono text-sm transition-colors flex items-center gap-2"
        style={{ color: 'var(--slate)' }}
        onMouseEnter={(e) => { e.currentTarget.style.color = 'var(--cream)' }}
        onMouseLeave={(e) => { e.currentTarget.style.color = 'var(--slate)' }}
      >
        ← Back to Dashboard
      </button>

      {/* Race Header */}
      <div 
        className="rounded-xl p-6"
        style={{
          background: 'var(--card)',
          border: '1px solid var(--border)',
          borderTop: '2px solid rgba(196,158,66,0.4)'
        }}
      >
        <div className="flex items-start justify-between flex-wrap gap-4">
          <div>
            <div className="flex items-center gap-3 mb-2 flex-wrap">
              <span className="font-display text-3xl font-bold" style={{ color: 'var(--cream)' }}>
                Race {race.raceNumber}
              </span>
              {race.grade && (
                <span className="font-mono text-xs px-2 py-1 rounded" style={{
                  background: 'rgba(196,158,66,0.1)',
                  color: 'var(--gold)',
                  border: '1px solid var(--border)'
                }}>
                  Grade {race.grade}
                </span>
              )}
              {hasResults && (
                <span className="font-mono text-xs px-3 py-1 rounded-full" style={{
                  background: 'var(--green-dim)',
                  color: 'var(--green)',
                  border: '1px solid rgba(60,184,122,0.25)'
                }}>
                  Final
                </span>
              )}
            </div>
            <div className="font-body text-lg mb-1" style={{ color: 'var(--slate)' }}>
              {race.raceName && race.raceName !== `Race ${race.raceNumber}`
                ? race.raceName
                : `${race.trackName} · Race ${race.raceNumber}`}
            </div>
            <div className="font-mono text-sm" style={{ color: 'var(--muted)' }}>
              {race.trackName} · {race.trackCode}
            </div>
          </div>
          <div className="text-right">
            <div className="font-display text-xl font-semibold mb-1" style={{ color: 'var(--gold)' }}>
              {formatPurse(race.purse)}
            </div>
            <div className="font-mono text-sm" style={{ color: 'var(--muted)' }}>Purse</div>
          </div>
        </div>

        {/* Race Details Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6 pt-6" style={{ borderTop: '1px solid var(--border)' }}>
          {[
            { label: 'Distance', value: formatDistance(race) },
            { label: 'Surface', value: race.surface || '—' },
            { label: 'Race Type', value: race.raceType || '—' },
            { label: 'Class', value: race.raceClass || '—' },
          ].map(item => (
            <div key={item.label}>
              <div className="font-mono text-xs tracking-[0.2em] uppercase mb-1" style={{ color: 'var(--muted)' }}>
                {item.label}
              </div>
              <div className="font-mono text-sm font-medium" style={{ color: 'var(--cream)' }}>{item.value}</div>
            </div>
          ))}
        </div>
      </div>

      {/* ML Model Badge */}
      {predictionsAvailable && (
        <div className="flex items-center gap-2 text-sm rounded-lg p-3" style={{
          background: 'rgba(60,184,122,0.06)',
          border: '1px solid rgba(60,184,122,0.2)'
        }}>
          <span className="w-2 h-2 rounded-full pulse" style={{ background: 'var(--green)' }} />
          <span className="font-mono font-medium" style={{ color: 'var(--green)' }}>
            ML Predictions Active
          </span>
          <span style={{ color: 'var(--muted)' }}>·</span>
          <span className="font-mono text-sm" style={{ color: 'var(--slate)' }}>
            Random Forest · 0.604 ROC-AUC · 55 Features
          </span>
        </div>
      )}

      {/* Runners */}
      <div className="space-y-3">
        {runners.map((runner, idx) => (
          <RunnerRow
            key={runner.runnerId}
            runner={runner}
            index={idx}
            isTopPick={runner.modelRank === 1 && predictionsAvailable}
            hasResults={hasResults}
          />
        ))}
      </div>

      {/* Model Accuracy Check (if results available) */}
      {hasResults && predictionsAvailable && winner && (
        <div 
          className="rounded-xl p-4 flex items-center gap-3"
          style={{
            background: modelCorrect ? 'rgba(60,184,122,0.06)' : 'rgba(224,75,53,0.06)',
            border: `1px solid ${modelCorrect ? 'rgba(60,184,122,0.3)' : 'rgba(224,75,53,0.3)'}`
          }}
        >
          <span className="text-2xl">{modelCorrect ? '✅' : '❌'}</span>
          <div>
            <div className="font-mono font-semibold" style={{
              color: modelCorrect ? 'var(--green)' : 'var(--live)'
            }}>
              {modelCorrect
                ? `✓ Model correctly predicted ${winner.horseName}!`
                : `✕ Model missed — ${winner.horseName} won (Model rank: ${winner.modelRank})`}
            </div>
            <div className="font-mono text-sm mt-1" style={{ color: 'var(--slate)' }}>
              Model confidence: {winner.winProbabilityNormalized
                ? `${(winner.winProbabilityNormalized * 100).toFixed(1)}%`
                : '—'}
            </div>
          </div>
        </div>
      )}

      {/* AI Chat */}
      <div className="mt-6">
        <h2 className="font-display text-lg font-semibold mb-3" style={{ color: 'var(--cream)' }}>
          Ask the AI Expert
        </h2>
        <ChatPanel
          raceId={parseInt(raceId)}
          dynamicHeight
          maxHeight={600}
          className="min-h-[320px] w-full"
        />
      </div>

    </div>
  )
}
