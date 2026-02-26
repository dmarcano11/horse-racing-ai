export default function ModelBadge() {
  return (
    <span 
      className="inline-flex items-center gap-1 font-mono text-xs tracking-[0.1em] rounded-full"
      style={{
        color: 'var(--gold)',
        background: 'rgba(196,158,66,0.1)',
        border: '1px solid rgba(196,158,66,0.2)',
        padding: '2px 8px'
      }}
    >
      ★ Model Top Pick
    </span>
  )
}