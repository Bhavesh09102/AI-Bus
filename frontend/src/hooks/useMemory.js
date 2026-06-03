import { useState, useEffect, useCallback } from 'react'

const API_BASE = 'http://localhost:5000'

function yesterdayISO() {
  const d = new Date()
  d.setDate(d.getDate() - 1)
  return d.toISOString()
}

function todayISO() {
  return new Date().toISOString()
}

export function useMemory() {
  const [working, setWorking] = useState({})
  const [episodic, setEpisodic] = useState([])
  const [loading, setLoading] = useState(true)

  const fetchWorking = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE}/memory/context`)
      if (res.ok) {
        const data = await res.json()
        setWorking(data)
      }
    } catch {
      /* backend offline */
    }
  }, [])

  const fetchEpisodic = useCallback(async () => {
    try {
      const since = encodeURIComponent(yesterdayISO())
      const until = encodeURIComponent(todayISO())
      const res = await fetch(
        `${API_BASE}/memory/recall?type=episodic&since=${since}&until=${until}`,
      )
      if (res.ok) {
        const data = await res.json()
        const results = data.results || []
        setEpisodic(results.slice(-5).reverse())
      }
    } catch {
      /* backend offline */
    }
  }, [])

  const refresh = useCallback(async () => {
    setLoading(true)
    await Promise.all([fetchWorking(), fetchEpisodic()])
    setLoading(false)
  }, [fetchWorking, fetchEpisodic])

  useEffect(() => {
    refresh()
    const t1 = setInterval(fetchWorking, 3000)
    const t2 = setInterval(fetchEpisodic, 10000)
    return () => {
      clearInterval(t1)
      clearInterval(t2)
    }
  }, [refresh, fetchWorking, fetchEpisodic])

  return { working, episodic, loading, refresh }
}
