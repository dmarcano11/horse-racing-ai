const variants = {
  blue:   'bg-blue-500/20 text-blue-400 border border-blue-500/30',
  green:  'bg-green-500/20 text-green-400 border border-green-500/30',
  amber:  'bg-amber-500/20 text-amber-400 border border-amber-500/30',
  red:    'bg-red-500/20 text-red-400 border border-red-500/30',
  slate:  'bg-slate-700 text-slate-300 border border-slate-600',
  // New status variants
  final:    'text-xs font-mono',
  live:     'text-xs font-mono',
  upcoming: 'text-xs font-mono',
}

export default function Badge({ children, variant = 'slate', className = '' }) {
  // Handle new status variants with inline styles
  if (variant === 'final') {
    return (
      <span 
        className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium font-mono ${className}`}
        style={{
          background: 'var(--green-dim)',
          color: 'var(--green)',
          border: '1px solid rgba(60,184,122,0.25)'
        }}
      >
        {children}
      </span>
    );
  }
  
  if (variant === 'live') {
    return (
      <span 
        className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium font-mono ${className}`}
        style={{
          background: 'var(--live-dim)',
          color: 'var(--live)',
          border: '1px solid rgba(224,75,53,0.3)'
        }}
      >
        <span className="mr-1">●</span>
        {children}
      </span>
    );
  }
  
  if (variant === 'upcoming') {
    return (
      <span 
        className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium font-mono ${className}`}
        style={{
          background: 'var(--blue-dim)',
          color: 'var(--blue)',
          border: '1px solid rgba(74,143,232,0.25)'
        }}
      >
        {children}
      </span>
    );
  }
  
  return (
    <span className={`
      inline-flex items-center px-2 py-0.5 rounded text-xs font-medium
      ${variants[variant]} ${className}
    `}>
      {children}
    </span>
  )
}