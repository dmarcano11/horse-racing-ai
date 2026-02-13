export default function ProbabilityBar({ probability, rank, runnerCount }) {
  if (!probability) return <span className="text-slate-500 text-sm">—</span>

  const pct = (probability * 100).toFixed(1)
  const width = Math.max(probability * 100, 2)

  const getColor = () => {
    if (rank === 1) return 'bg-blue-500'
    if (rank === 2) return 'bg-blue-400'
    if (rank === 3) return 'bg-slate-400'
    return 'bg-slate-600'
  }

  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 bg-slate-700 rounded-full h-2 overflow-hidden">
        <div
          className={`h-full rounded-full transition-all ${getColor()}`}
          style={{ width: `${width}%` }}
        />
      </div>
      <span className="text-sm font-mono text-slate-300 w-10 text-right">
        {pct}%
      </span>
    </div>
  )
}