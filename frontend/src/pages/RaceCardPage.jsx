import { useParams, useNavigate } from 'react-router-dom'
import { useRaceCard } from '../hooks/usePredictions'
import LoadingSpinner from '../components/ui/LoadingSpinner'
import ErrorMessage from '../components/ui/ErrorMessage'
import Badge from '../components/ui/Badge'
import ProbabilityBar from '../components/predictions/ProbabilityBar'
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

  return (
    <div className="space-y-6">

      {/* Back Button */}
      <button
        onClick={() => navigate(-1)}
        className="text-slate-400 hover:text-white text-sm transition-colors
                   flex items-center gap-2"
      >
        ← Back to Dashboard
      </button>

      {/* Race Header */}
      <div className="bg-slate-800 rounded-xl border border-slate-700 p-6">
        <div className="flex items-start justify-between">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <span className="text-3xl font-bold text-white">
                Race {race.raceNumber}
              </span>
              {race.grade && (
                <Badge variant="amber">Grade {race.grade}</Badge>
              )}
              {hasResults && <Badge variant="green">Final</Badge>}
            </div>
            <div className="text-slate-300 text-lg">
              {race.raceName && race.raceName !== `Race ${race.raceNumber}`
                ? race.raceName
                : `${race.trackName} · Race ${race.raceNumber}`}
            </div>
            <div className="text-slate-400 text-sm mt-1">
              {race.trackName} · {race.trackCode}
            </div>
          </div>
          <div className="text-right space-y-1">
            <div className="text-white font-semibold text-lg">
              {formatPurse(race.purse)}
            </div>
            <div className="text-slate-400 text-sm">Purse</div>
          </div>
        </div>

        {/* Race Details Grid */}
        <div className="grid grid-cols-4 gap-4 mt-6 pt-6 border-t border-slate-700">
          {[
            { label: 'Distance', value: formatDistance(race) },
            { label: 'Surface', value: race.surface || '—' },
            { label: 'Race Type', value: race.raceType || '—' },
            { label: 'Class', value: race.raceClass || '—' },
          ].map(item => (
            <div key={item.label}>
              <div className="text-slate-400 text-xs uppercase tracking-wider mb-1">
                {item.label}
              </div>
              <div className="text-white font-medium">{item.value}</div>
            </div>
          ))}
        </div>
      </div>

      {/* ML Model Badge */}
      {predictionsAvailable && (
        <div className="flex items-center gap-2 text-sm">
          <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
          <span className="text-green-400 font-medium">
            ML Predictions Active
          </span>
          <span className="text-slate-500">·</span>
          <span className="text-slate-400">
            Random Forest · 0.604 ROC-AUC · 55 Features
          </span>
        </div>
      )}

      {/* Runners Table */}
      <div className="bg-slate-800 rounded-xl border border-slate-700 overflow-hidden">

        {/* Table Header */}
        <div className={`grid gap-4 px-6 py-3 bg-slate-900/50 border-b
                        border-slate-700 text-xs font-medium text-slate-400
                        uppercase tracking-wider
                        ${hasResults
            ? 'grid-cols-12'
            : 'grid-cols-10'}`}>
          <div className="col-span-1">#</div>
          <div className="col-span-3">Horse</div>
          <div className="col-span-2">Jockey / Trainer</div>
          <div className="col-span-1">ML Odds</div>
          {predictionsAvailable && (
            <div className="col-span-3">AI Win Probability</div>
          )}
          {hasResults && <div className="col-span-2">Result</div>}
        </div>

        {/* Runner Rows */}
        {runners.map((runner, idx) => (
          <div
            key={runner.runnerId}
            className={`grid gap-4 px-6 py-4 items-center
                        ${hasResults ? 'grid-cols-12' : 'grid-cols-10'}
                        ${runner.finishPosition === 1
                ? 'bg-amber-500/5 border-l-2 border-amber-500'
                : ''}
                        ${idx !== runners.length - 1
                ? 'border-b border-slate-700/50' : ''}`}
          >
            {/* Post Position */}
            <div className="col-span-1">
              <span className={`w-8 h-8 rounded-full flex items-center
                               justify-center text-sm font-bold
                               ${runner.modelRank === 1
                  ? 'bg-blue-600 text-white'
                  : 'bg-slate-700 text-slate-300'}`}>
                {runner.postPosition || runner.programNumber || idx + 1}
              </span>
            </div>

            {/* Horse Name */}
            <div className="col-span-3">
              <div className="text-white font-semibold text-sm">
                {runner.horseName}
              </div>
              {runner.modelRank === 1 && predictionsAvailable && (
                <div className="text-blue-400 text-xs mt-0.5">
                  ⭐ Model Top Pick
                </div>
              )}
              {runner.isScratched && (
                <Badge variant="red" className="mt-1">Scratched</Badge>
              )}
            </div>

            {/* Jockey / Trainer */}
            <div className="col-span-2">
              <div className="text-slate-300 text-xs">
                {runner.jockeyName || '—'}
              </div>
              <div className="text-slate-500 text-xs mt-0.5">
                {runner.trainerName || '—'}
              </div>
            </div>

            {/* Morning Line Odds */}
            <div className="col-span-1">
              <span className="text-slate-300 text-sm font-mono">
                {runner.morningLineOdds || '—'}
              </span>
            </div>

            {/* AI Probability Bar */}
            {predictionsAvailable && (
              <div className="col-span-3">
                <ProbabilityBar
                  probability={runner.winProbabilityNormalized}
                  rank={runner.modelRank}
                  runnerCount={runners.length}
                />
              </div>
            )}

            {/* Result */}
            {hasResults && (
              <div className="col-span-2">
                {runner.finishPosition ? (
                  <div className="flex items-center gap-2">
                    <span className={`w-6 h-6 rounded-full flex items-center
                                     justify-center text-xs font-bold
                                     ${runner.finishPosition === 1
                        ? 'bg-amber-500 text-black'
                        : runner.finishPosition === 2
                          ? 'bg-slate-400 text-black'
                          : runner.finishPosition === 3
                            ? 'bg-amber-700 text-white'
                            : 'bg-slate-700 text-slate-300'}`}>
                      {runner.finishPosition}
                    </span>
                    {runner.winPayoff && (
                      <span className="text-green-400 text-xs font-mono">
                        ${runner.winPayoff.toFixed(2)}
                      </span>
                    )}
                  </div>
                ) : (
                  <span className="text-slate-500 text-sm">—</span>
                )}
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Model Accuracy Check (if results available) */}
      {hasResults && predictionsAvailable && (() => {
        const winner = runners.find(r => r.finishPosition === 1)
        const modelPicked = winner?.modelRank === 1
        return (
          <div className={`rounded-xl border p-4 flex items-center gap-3
                          ${modelPicked
              ? 'bg-green-500/10 border-green-500/30'
              : 'bg-slate-800 border-slate-700'}`}>
            <span className="text-2xl">{modelPicked ? '✅' : '❌'}</span>
            <div>
              <div className={`font-semibold
                              ${modelPicked ? 'text-green-400' : 'text-slate-300'}`}>
                {modelPicked
                  ? `Model correctly predicted ${winner?.horseName}!`
                  : `Model missed - ${winner?.horseName} won (Model rank: ${winner?.modelRank})`}
              </div>
              <div className="text-slate-400 text-sm">
                Model confidence: {winner
                  ? `${((winner.winProbabilityNormalized || 0) * 100).toFixed(1)}%`
                  : '—'}
              </div>
            </div>
          </div>
        )
      })()}

      {/* AI Chat */}
      <div className="mt-6">
        <h2 className="text-lg font-semibold text-white mb-3">
          Ask the AI Expert
        </h2>
        <ChatPanel raceId={parseInt(raceId)} className="h-full" />
      </div>

    </div>
  )
}