import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { format, subDays, addDays } from 'date-fns'
import { useRaces } from '../hooks/useRaces'
import LoadingSpinner from '../components/ui/LoadingSpinner'
import ErrorMessage from '../components/ui/ErrorMessage'
import Badge from '../components/ui/Badge'

export default function ResultsPage() {
	const [selectedDate, setSelectedDate] = useState(new Date('2026-02-07'))
	const [selectedTrack, setSelectedTrack] = useState();
	const { races, loading, error } = useRaces(selectedDate)
	const navigate = useNavigate()

	const completedRaces = races.filter(r => r.hasResults)

	// Group by track
	const racesByTrack = completedRaces.reduce((acc, race) => {
		const track = race.trackName
		if (!acc[track]) acc[track] = []
		acc[track].push(race)
		return acc
	}, {})

	const tracks = Object.keys(racesByTrack).sort()
	const activeTrack = selectedTrack || tracks[0]
	const activeRaces = racesByTrack[activeTrack] || []

	return (
		<div className="space-y-6">

			{/* Header */}
			<div className="flex items-center justify-between">
				<div>
					<h1 className="text-2xl font-bold text-white">Results</h1>
					<p className="text-slate-400 text-sm mt-1">
						{completedRaces.length} completed races
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

			{loading && <LoadingSpinner message="Loading results..." />}
			{error && <ErrorMessage message={error} />}

			{!loading && completedRaces.length === 0 && (
				<div className="text-center py-20 text-slate-400">
					No completed races found for {format(selectedDate, 'MMMM d, yyyy')}
				</div>
			)}

			{/* Results Grid */}
			{!loading && tracks.length > 0 && (
				<div className="space-y-4">
					{/* Track Tabs */}
					<div className="flex flex-wrap gap-2">
						{tracks.map(track => (
							<button
								key={track}
								onClick={() => setSelectedTrack(track)}
								className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${track === activeTrack
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

					{/* Results Grid - filtered by track */}
					<div className="grid grid-cols-1 gap-4">
						{activeRaces.map(race => (
							<div
								key={race.id}
								onClick={() => navigate(`/races/${race.id}`)}
								className="bg-slate-800 rounded-xl border border-slate-700 p-5
                     hover:border-slate-600 hover:bg-slate-700/50
                     transition-all cursor-pointer"
							>
								<div className="flex items-center justify-between">
									<div className="flex items-center gap-3">
										<span className="w-8 h-8 rounded-full bg-slate-700 flex items-center
                               justify-center text-sm font-bold text-white">
											{race.raceNumber}
										</span>
										<div>
											<div className="text-white font-semibold">
												{race.raceName && race.raceName !== `Race ${race.raceNumber}`
													? race.raceName
													: `Race ${race.raceNumber}`}
											</div>
											<div className="text-slate-400 text-sm">
												{race.distanceValue}{race.distanceUnit} · {race.surface}
												{race.purse && ` · $${race.purse.toLocaleString()}`}
											</div>
										</div>
									</div>
									<div className="flex items-center gap-3">
										<Badge variant="green">Final</Badge>
										<span className="text-blue-400 text-sm">View Details →</span>
									</div>
								</div>
							</div>
						))}
					</div>
				</div>
			)}

		</div>
	)
}