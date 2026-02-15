export default function TrackTabs({ tracks, activeTrack, onChange }) {
  return (
    <div className="flex flex-wrap gap-2 mb-6">
      {tracks.map(track => {
        const isActive = track.id === activeTrack;
        return (
          <button
            key={track.id}
            onClick={() => onChange(track.id)}
            className="inline-flex items-center gap-2 font-mono text-[12px] tracking-[0.08em] rounded-full px-4 py-2 transition-all duration-200 cursor-pointer"
            style={{
              background: isActive ? 'rgba(196,158,66,0.10)' : 'var(--card)',
              border: `1px solid ${isActive ? 'var(--gold)' : 'var(--border)'}`,
              color: isActive ? 'var(--gold)' : 'var(--slate)',
            }}
          >
            {track.name}
            <span 
              className="rounded-full px-2 py-0.5 text-[11px]"
              style={{
                background: isActive ? 'rgba(196,158,66,0.2)' : 'rgba(255,255,255,0.07)',
                color: isActive ? 'var(--gold-light)' : 'var(--muted)',
              }}
            >
              {track.count}
            </span>
          </button>
        );
      })}
    </div>
  );
}
