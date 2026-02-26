import ProbabilityBar from '../predictions/ProbabilityBar'
import ModelBadge from '../predictions/ModelBadge'

export default function RunnerRow({ runner, index, isTopPick, hasResults }) {
  return (
    <div
      className="fade-up"
      style={{
        background: isTopPick ? 'rgba(74,143,232,0.04)' : 'var(--card)',
        border: `1px solid ${isTopPick ? 'rgba(74,143,232,0.35)' : 'var(--border)'}`,
        borderRadius: '8px',
        padding: '16px 20px',
        display: 'grid',
        gridTemplateColumns: '50px 1fr 160px 90px 1fr 72px',
        gap: '12px',
        alignItems: 'center',
        transition: 'all 0.25s',
        animationDelay: `${index * 0.04}s`,
        cursor: 'pointer'
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.borderColor = 'var(--border-hi)'
        e.currentTarget.style.background = isTopPick ? 'rgba(74,143,232,0.06)' : 'var(--card-hi)'
        e.currentTarget.style.transform = 'translateX(3px)'
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.borderColor = isTopPick ? 'rgba(74,143,232,0.35)' : 'var(--border)'
        e.currentTarget.style.background = isTopPick ? 'rgba(74,143,232,0.04)' : 'var(--card)'
        e.currentTarget.style.transform = 'translateX(0)'
      }}
    >
      {/* Number Circle */}
      <div
        className="flex items-center justify-center rounded-full font-mono text-sm font-semibold"
        style={{
          width: '36px',
          height: '36px',
          background: isTopPick ? 'var(--blue-dim)' : 'var(--surface)',
          border: `1px solid ${isTopPick ? 'var(--blue)' : 'var(--border)'}`,
          color: isTopPick ? 'var(--blue)' : 'var(--slate)'
        }}
      >
        {runner.postPosition || runner.programNumber || index + 1}
      </div>

      {/* Horse Name */}
      <div>
        <div className="font-display text-base font-semibold" style={{ color: 'var(--cream)' }}>
          {runner.horseName}
        </div>
        {isTopPick && <ModelBadge />}
      </div>

      {/* Jockey / Trainer */}
      <div>
        <div className="font-mono text-sm" style={{ color: 'var(--cream)' }}>
          {runner.jockeyName || '—'}
        </div>
        <div className="font-mono text-xs mt-0.5" style={{ color: 'var(--muted)' }}>
          {runner.trainerName || '—'}
        </div>
      </div>

      {/* Odds */}
      <div className="font-mono text-sm" style={{ color: 'var(--cream)' }}>
        {runner.morningLineOdds || '—'}
      </div>

      {/* Probability Bar */}
      <div>
        <ProbabilityBar
          probability={runner.winProbabilityNormalized}
          rank={runner.modelRank}
          runnerCount={runner.runnerCount}
        />
      </div>

      {/* Result */}
      <div>
        {hasResults && runner.finishPosition ? (
          <div className="flex items-center justify-center">
            <div
              className="flex items-center justify-center rounded-full font-bold text-xs"
              style={{
                width: '28px',
                height: '28px',
                background:
                  runner.finishPosition === 1 ? '#FFD700' :
                  runner.finishPosition === 2 ? '#C0C0C0' :
                  runner.finishPosition === 3 ? '#CD7F32' :
                  'var(--surface)',
                color:
                  runner.finishPosition <= 3 ? '#000' : 'var(--slate)',
                border: runner.finishPosition <= 3 ? 'none' : '1px solid var(--border)'
              }}
            >
              {runner.finishPosition}
            </div>
          </div>
        ) : null}
      </div>
    </div>
  )
}
