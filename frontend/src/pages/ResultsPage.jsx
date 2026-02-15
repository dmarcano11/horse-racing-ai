import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { format, subDays, addDays } from 'date-fns'
import { useRaces } from '../hooks/useRaces'
import LoadingSpinner from '../components/ui/LoadingSpinner'
import ErrorMessage from '../components/ui/ErrorMessage'
import TrackTabs from '../components/ui/TrackTabs'

export default function ResultsPage() {
	const [selectedDate, setSelectedDate] = useState(new Date('2026-02-07'))
	const [selectedTrack, setSelectedTrack] = useState()
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
						Results
					</h1>
					<p className="font-mono text-[10px]" style={{ color: 'var(--muted)' }}>
						{completedRaces.length} completed races
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

			{loading && <LoadingSpinner message="Loading results..." />}
			{error && <ErrorMessage message={error} />}

			{!loading && completedRaces.length === 0 && (
				<div className="text-center py-20 font-body" style={{ color: 'var(--slate)' }}>
					No completed races found for {format(selectedDate, 'MMMM d, yyyy')}
				</div>
			)}

			{/* Results Grid */}
			{!loading && tracks.length > 0 && (
				<div className="space-y-6">
					{/* Track Tabs */}
					<TrackTabs 
						tracks={tracks} 
						activeTrack={activeTrack} 
						onChange={setSelectedTrack} 
					/>

					{/* Results Grid */}
					<div className="grid grid-cols-1 gap-4">
						{activeRaces.map(race => (
							<div
								key={race.id}
								onClick={() => navigate(`/races/${race.id}`)}
								className="rounded-xl p-5 cursor-pointer transition-all"
								style={{
									background: 'var(--card)',
									border: '1px solid var(--border)'
								}}
								onMouseEnter={(e) => {
									e.currentTarget.style.borderColor = 'var(--border-hi)'
									e.currentTarget.style.background = 'var(--card-hi)'
									e.currentTarget.style.transform = 'translateY(-2px)'
								}}
								onMouseLeave={(e) => {
									e.currentTarget.style.borderColor = 'var(--border)'
									e.currentTarget.style.background = 'var(--card)'
									e.currentTarget.style.transform = 'translateY(0)'
								}}
							>
								<div className="flex items-center justify-between">
									<div className="flex items-center gap-3">
										<span 
											className="w-8 h-8 rounded-full flex items-center justify-center font-mono text-sm font-bold"
											style={{
												background: 'var(--surface)',
												border: '1px solid var(--border)',
												color: 'var(--cream)'
											}}
										>
											{race.raceNumber}
										</span>
										<div>
											<div className="font-body font-semibold" style={{ color: 'var(--cream)' }}>
												{race.raceName && race.raceName !== `Race ${race.raceNumber}`
													? race.raceName
													: `Race ${race.raceNumber}`}
											</div>
											<div className="font-mono text-sm" style={{ color: 'var(--slate)' }}>
												{race.distanceValue}{race.distanceUnit} · {race.surface}
												{race.purse && ` · $${race.purse.toLocaleString()}`}
											</div>
										</div>
									</div>
									<div className="flex items-center gap-3">
										<span className="font-mono text-[8px] px-3 py-1 rounded-full" style={{
											background: 'var(--green-dim)',
											color: 'var(--green)',
											border: '1px solid rgba(60,184,122,0.25)'
										}}>
											Final
										</span>
										<span className="font-mono text-sm" style={{ color: 'var(--gold)' }}>
											View Details →
										</span>
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