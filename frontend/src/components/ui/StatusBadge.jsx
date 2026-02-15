export default function StatusBadge({ status }) {
  const variants = {
    final: { 
      label: 'Final', 
      bg: 'var(--green-dim)', 
      color: 'var(--green)', 
      border: 'rgba(60,184,122,0.25)' 
    },
    live: { 
      label: '● LIVE', 
      bg: 'var(--live-dim)', 
      color: 'var(--live)', 
      border: 'rgba(224,75,53,0.3)' 
    },
    upcoming: { 
      label: 'Upcoming', 
      bg: 'var(--blue-dim)', 
      color: 'var(--blue)', 
      border: 'rgba(74,143,232,0.25)' 
    },
  };
  
  const v = variants[status] ?? variants.upcoming;
  
  return (
    <span 
      className="inline-flex items-center font-mono text-[8px] tracking-[0.08em] font-semibold rounded-full px-3 py-1"
      style={{
        background: v.bg, 
        color: v.color,
        border: `1px solid ${v.border}`,
      }}
    >
      {v.label}
    </span>
  );
}
