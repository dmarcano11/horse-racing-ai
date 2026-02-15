import { useState } from 'react'
import { format, subDays, addDays } from 'date-fns'
import { useRaces } from '../hooks/useRaces'
import LoadingSpinner from '../components/ui/LoadingSpinner'
import ErrorMessage from '../components/ui/ErrorMessage'
import TrackTabs from '../components/ui/TrackTabs'
import RaceList from '../components/races/RaceList'

export default function Dashboard() {
  const [selectedDate, setSelectedDate] = useState(new Date('2026-02-07'))
  const [selectedTrack, setSelectedTrack] = useState(null)
  const { races, loading, error } = useRaces(selectedDate)

  // Group races by track
  const racesByTrack = races.reduce((acc, race) => {
    const track = race.trackName
    if (!acc[track]) acc[track] = []
    acc[track].push(race)
    return acc
  }, {})

  const tracks = Object.keys(racesByTrack).sort().map(name => ({
    id: name,
    name,
    count: racesByTrack[name].length
  }))
  
  const activeTrack = selectedTrack || tracks[0]?.id
  const activeRaces = activeTrack ? racesByTrack[activeTrack] || [] : []

  return (
    <div className="space-y-6">

      {/* Header */}
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <h1 className="font-display text-3xl mb-2" style={{ color: 'var(--cream)' }}>
            Race Dashboard
          </h1>
          <p className="font-mono text-[10px]" style={{ color: 'var(--muted)' }}>
            {races.length} races across {tracks.length} tracks
          </p>
        </div>

        {/* Date Navigator */}
        <div className="flex items-center gap-2">
          <button
            onClick={() => setSelectedDate(d => subDays(d, 1))}
            className="p-2 rounded-lg transition-colors font-mono"
            style={{
              background: 'var(--card)',
              border: '1px solid var(--border)',
              color: 'var(--slate)'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = 'var(--card-hi)'
              e.currentTarget.style.color = 'var(--cream)'
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = 'var(--card)'
              e.currentTarget.style.color = 'var(--slate)'
            }}
          >
            ←
          </button>
          <input
            type="date"
            value={format(selectedDate, 'yyyy-MM-dd')}
            onChange={e => setSelectedDate(new Date(e.target.value + 'T12:00:00'))}
            className="rounded-lg px-3 py-2 text-sm font-mono"
            style={{
              background: 'var(--card)',
              border: '1px solid var(--border)',
              color: 'var(--cream)',
              outline: 'none'
            }}
          />
          <button
            onClick={() => setSelectedDate(d => addDays(d, 1))}
            className="p-2 rounded-lg transition-colors font-mono"
            style={{
              background: 'var(--card)',
              border: '1px solid var(--border)',
              color: 'var(--slate)'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = 'var(--card-hi)'
              e.currentTarget.style.color = 'var(--cream)'
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = 'var(--card)'
              e.currentTarget.style.color = 'var(--slate)'
            }}
          >
            →
          </button>
        </div>
      </div>

      {loading && <LoadingSpinner message="Loading races..." />}
      {error && <ErrorMessage message={error} />}

      {!loading && !error && tracks.length === 0 && (
        <div className="text-center py-20 font-body" style={{ color: 'var(--slate)' }}>
          No races found for {format(selectedDate, 'MMMM d, yyyy')}
        </div>
      )}

      {!loading && tracks.length > 0 && (
        <div className="space-y-6">
          {/* Track Tabs */}
          <TrackTabs 
            tracks={tracks} 
            activeTrack={activeTrack} 
            onChange={setSelectedTrack} 
          />

          {/* Race List */}
          <RaceList races={activeRaces} />

          {/* Summary Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[
              { label: 'Total Races', value: races.length },
              { label: 'Tracks Today', value: tracks.length },
              {
                label: 'Completed',
                value: races.filter(r => r.hasResults).length
              },
              {
                label: 'Upcoming',
                value: races.filter(r => !r.hasResults).length
              },
            ].map(stat => (
              <div 
                key={stat.label}
                className="rounded-xl p-4"
                style={{
                  background: 'var(--card)',
                  border: '1px solid var(--border)'
                }}
              >
                <div className="font-display text-2xl font-bold mb-1" style={{ color: 'var(--cream)' }}>
                  {stat.value}
                </div>
                <div className="font-mono text-[9px]" style={{ color: 'var(--muted)' }}>
                  {stat.label}
                </div>
              </div>
            ))}
          </div>

        </div>
      )}
    </div>
  )
}
