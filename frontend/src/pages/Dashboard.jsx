import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { format, subDays, addDays } from 'date-fns'
import { useRaces } from '../hooks/useRaces'
import LoadingSpinner from '../components/ui/LoadingSpinner'
import ErrorMessage from '../components/ui/ErrorMessage'
import Badge from '../components/ui/Badge'

export default function Dashboard() {
  const [selectedDate, setSelectedDate] = useState(new Date('2026-02-07'))
  const [selectedTrack, setSelectedTrack] = useState(null)
  const { races, meets, loading, error } = useRaces(selectedDate)
  const navigate = useNavigate()

  // Group races by track
  const racesByTrack = races.reduce((acc, race) => {
    const track = race.trackName
    if (!acc[track]) acc[track] = []
    acc[track].push(race)
    return acc
  }, {})

  const tracks = Object.keys(racesByTrack).sort()
  const activeTrack = selectedTrack || tracks[0]
  const activeRaces = racesByTrack[activeTrack] || []

  const formatDistance = (race) => {
    if (!race.distanceValue) return '—'
    const furlongs = race.distanceUnit === 'F'
      ? race.distanceValue
      : (race.distanceValue / 201.168).toFixed(1)
    return `${furlongs}F`
  }

  const formatPurse = (purse) => {
    if (!purse) return '—'
    return `$${(purse / 1000).toFixed(0)}k`
  }

  const getSurfaceBadge = (surface) => {
    if (!surface) return null
    const s = surface.toLowerCase()
    if (s.includes('turf')) return <Badge variant="green">Turf</Badge>
    if (s.includes('dirt')) return <Badge variant="amber">Dirt</Badge>
    return <Badge variant="slate">{surface}</Badge>
  }

  const getStatusBadge = (race) => {
    if (race.hasResults) return <Badge variant="green">Final</Badge>
    if (race.hasFinished) return <Badge variant="blue">Official</Badge>
    return <Badge variant="slate">Scheduled</Badge>
  }

  return (
    <div className="space-y-6">

      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Race Dashboard</h1>
          <p className="text-slate-400 text-sm mt-1">
            {races.length} races across {tracks.length} tracks
          </p>
        </div>

        {/* Date Navigator */}
        <div className="flex items-center gap-2">
          <button
            onClick={() => setSelectedDate(d => subDays(d, 1))}
            className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700
                       text-slate-400 hover:text-white transition-colors"
          >
            ←
          </button>
          <input
            type="date"
            value={format(selectedDate, 'yyyy-MM-dd')}
            onChange={e => setSelectedDate(new Date(e.target.value + 'T12:00:00'))}
            className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-2
                       text-white text-sm focus:outline-none focus:border-blue-500"
          />
          <button
            onClick={() => setSelectedDate(d => addDays(d, 1))}
            className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700
                       text-slate-400 hover:text-white transition-colors"
          >
            →
          </button>
        </div>
      </div>

      {loading && <LoadingSpinner message="Loading races..." />}
      {error && <ErrorMessage message={error} />}

      {!loading && !error && tracks.length === 0 && (
        <div className="text-center py-20 text-slate-400">
          No races found for {format(selectedDate, 'MMMM d, yyyy')}
        </div>
      )}

      {!loading && tracks.length > 0 && (
        <div className="space-y-4">

          {/* Track Tabs */}
          <div className="flex flex-wrap gap-2">
            {tracks.map(track => (
              <button
                key={track}
                onClick={() => setSelectedTrack(track)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  track === activeTrack
                    ? 'bg-blue-600 text-white'
                    : 'bg-slate-800 text-slate-400 hover:text-white hover:bg-slate-700'
                }`}
              >
                {track}
                <span className="ml-2 text-xs opacity-70">
                  {racesByTrack[track].length}
                </span>
              </button>
            ))}
          </div>

          {/* Race Table */}
          <div className="bg-slate-800 rounded-xl border border-slate-700 overflow-hidden">

            {/* Table Header */}
            <div className="grid grid-cols-12 gap-4 px-6 py-3 bg-slate-900/50
                            border-b border-slate-700 text-xs font-medium
                            text-slate-400 uppercase tracking-wider">
              <div className="col-span-1">Race</div>
              <div className="col-span-3">Name</div>
              <div className="col-span-2">Distance</div>
              <div className="col-span-2">Surface</div>
              <div className="col-span-2">Purse</div>
              <div className="col-span-1">Status</div>
              <div className="col-span-1"></div>
            </div>

            {/* Race Rows */}
            {activeRaces.map((race, idx) => (
              <div
                key={race.id}
                className={`grid grid-cols-12 gap-4 px-6 py-4 items-center
                            hover:bg-slate-700/50 transition-colors cursor-pointer
                            ${idx !== activeRaces.length - 1
                              ? 'border-b border-slate-700/50' : ''}`}
                onClick={() => navigate(`/races/${race.id}`)}
              >
                <div className="col-span-1">
                  <span className="w-8 h-8 rounded-full bg-slate-700 flex items-center
                                   justify-center text-sm font-bold text-white">
                    {race.raceNumber}
                  </span>
                </div>

                <div className="col-span-3">
                  <div className="text-white font-medium text-sm">
                    {race.raceName || `Race ${race.raceNumber}`}
                  </div>
                  <div className="text-slate-400 text-xs mt-0.5">
                    {race.raceClass || race.raceType || '—'}
                  </div>
                </div>

                <div className="col-span-2 text-slate-300 text-sm">
                  {formatDistance(race)}
                </div>

                <div className="col-span-2">
                  {getSurfaceBadge(race.surface)}
                </div>

                <div className="col-span-2 text-slate-300 text-sm font-medium">
                  {formatPurse(race.purse)}
                </div>

                <div className="col-span-1">
                  {getStatusBadge(race)}
                </div>

                <div className="col-span-1 text-right">
                  <span className="text-blue-400 text-sm hover:text-blue-300">
                    View →
                  </span>
                </div>
              </div>
            ))}
          </div>

          {/* Summary Stats */}
          <div className="grid grid-cols-4 gap-4">
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
              <div key={stat.label}
                   className="bg-slate-800 rounded-xl border border-slate-700 p-4">
                <div className="text-2xl font-bold text-white">{stat.value}</div>
                <div className="text-slate-400 text-sm mt-1">{stat.label}</div>
              </div>
            ))}
          </div>

        </div>
      )}
    </div>
  )
}