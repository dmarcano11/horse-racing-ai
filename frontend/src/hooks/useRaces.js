import { useState, useEffect } from 'react'
import { getRacesByDate, getMeetsByDate } from '../services/api'
import { format } from 'date-fns'

export function useRaces(date) {
  const [races, setRaces] = useState([])
  const [meets, setMeets] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const dateStr = format(date, 'yyyy-MM-dd')

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true)
      setError(null)
      try {
        const [racesRes, meetsRes] = await Promise.all([
          getRacesByDate(dateStr),
          getMeetsByDate(dateStr)
        ])
        setRaces(racesRes.data)
        setMeets(meetsRes.data)
      } catch (err) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [dateStr])

  return { races, meets, loading, error }
}