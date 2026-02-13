const variants = {
  blue:   'bg-blue-500/20 text-blue-400 border border-blue-500/30',
  green:  'bg-green-500/20 text-green-400 border border-green-500/30',
  amber:  'bg-amber-500/20 text-amber-400 border border-amber-500/30',
  red:    'bg-red-500/20 text-red-400 border border-red-500/30',
  slate:  'bg-slate-700 text-slate-300 border border-slate-600',
}

export default function Badge({ children, variant = 'slate', className = '' }) {
  return (
    <span className={`
      inline-flex items-center px-2 py-0.5 rounded text-xs font-medium
      ${variants[variant]} ${className}
    `}>
      {children}
    </span>
  )
}