export default function SurfaceBadge({ surface }) {
  const isDirt = surface?.toLowerCase() === 'dirt';
  
  return (
    <span 
      className="inline-flex items-center font-mono text-[9px] font-semibold tracking-[0.08em] rounded px-2 py-0.5"
      style={{
        background: isDirt ? 'rgba(180,120,40,0.2)' : 'var(--green-dim)',
        color: isDirt ? '#E8A040' : 'var(--green)',
        border: `1px solid ${isDirt ? 'rgba(180,120,40,0.3)' : 'rgba(60,184,122,0.25)'}`,
      }}
    >
      {surface}
    </span>
  );
}
