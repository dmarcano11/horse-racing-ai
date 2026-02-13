import { useState, useEffect } from 'react'
import { getRaceCard } from '../services/api'

export function useRaceCard(raceId) {
  const [raceCard, setRaceCard] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (!raceId) return
    const fetchData = async () => {
      setLoading(true)
      setError(null)
      try {
        const res = await getRaceCard(raceId, true)
        setRaceCard(res.data)
      } catch (err) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [raceId])

  return { raceCard, loading, error }
}