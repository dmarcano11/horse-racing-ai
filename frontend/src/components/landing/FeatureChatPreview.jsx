import { useNavigate } from 'react-router-dom'

export default function FeatureChatPreview() {
  const navigate = useNavigate()

  return (
    <div 
      onClick={() => navigate('/chat')}
      className="cursor-pointer rounded-2xl overflow-hidden transition-all"
      style={{
        background: 'var(--obsidian)',
        border: '1px solid rgba(196,158,66,0.12)',
      }}
    >
      {/* Header */}
      <div className="px-4 py-3 flex items-center gap-3" style={{ borderBottom: '1px solid var(--border)' }}>
        <div className="relative">
          <div className="w-8 h-8 rounded-full flex items-center justify-center" style={{ border: '2px solid var(--gold)', background: 'var(--surface)' }}>♟</div>
          <div className="absolute bottom-0 right-0 w-2 h-2 rounded-full" style={{ background: 'var(--green)', border: '2px solid var(--obsidian)' }} />
        </div>
        <div>
          <div className="font-display text-sm" style={{ color: 'var(--cream)' }}>AI Racing Expert</div>
          <div className="font-mono text-[7px]" style={{ color: 'var(--muted)' }}>Online · Ready</div>
        </div>
      </div>

      {/* Messages */}
      <div className="p-4 space-y-3" style={{ minHeight: '280px' }}>
        {/* User Message */}
        <div className="flex justify-end">
          <div className="max-w-[85%] px-3 py-2 rounded-lg font-body text-xs" style={{
            background: 'rgba(196,158,66,0.10)',
            border: '1px solid var(--border-hi)',
            color: 'var(--cream)'
          }}>
            What's the best bet in the 3rd race at Gulfstream?
          </div>
        </div>

        {/* AI Response */}
        <div className="flex justify-start">
          <div className="max-w-[85%] px-3 py-2.5 rounded-lg font-body text-xs leading-relaxed" style={{
            background: 'var(--card)',
            border: '1px solid var(--border)',
            color: 'rgba(237,228,204,0.88)'
          }}>
            <p className="mb-2">Based on the ML model, <strong style={{ color: 'var(--gold)' }}>Horse #5 (Midnight Thunder)</strong> has the highest win probability at 28.4%.</p>
            <p className="mb-2">Key factors: Strong jockey form (85%), ideal distance, and excellent surface history on dirt.</p>
            <div className="mt-3 p-2 rounded" style={{ background: 'rgba(74,143,232,0.08)', border: '1px solid rgba(74,143,232,0.2)' }}>
              <div className="font-mono text-[9px] mb-1" style={{ color: 'var(--blue)' }}>ML Win Probability</div>
              <div className="font-mono text-lg font-bold" style={{ color: 'var(--gold)' }}>28.4%</div>
            </div>
          </div>
        </div>
      </div>

      {/* Hover Hint */}
      <div className="px-4 py-2 text-center font-mono text-[9px]" style={{ color: 'var(--gold)', borderTop: '1px solid var(--border)' }}>
        Click to try the AI Expert →
      </div>
    </div>
  )
}
