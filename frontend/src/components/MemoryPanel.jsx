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

function formatRelative(iso) {
  if (!iso) return ''
  const then = new Date(iso).getTime()
  const diff = Date.now() - then
  const mins = Math.floor(diff / 60000)
  if (mins < 1) return 'just now'
  if (mins < 60) return `${mins}m ago`
  const hrs = Math.floor(mins / 60)
  if (hrs < 24) return `${hrs}h ago`
  return `${Math.floor(hrs / 24)}d ago`
}

export default function MemoryPanel() {
  const [working, setWorking] = useState({})
  const [episodic, setEpisodic] = useState([])
  const [info, setInfo] = useState({ working_memory_keys: 0, uptime_seconds: 0 })

  const fetchContext = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE}/memory/context`)
      if (res.ok) setWorking(await res.json())
    } catch {
      /* offline */
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
      /* offline */
    }
  }, [])

  const fetchInfo = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE}/info`)
      if (res.ok) setInfo(await res.json())
    } catch {
      /* offline */
    }
  }, [])

  const handleFlush = async () => {
    try {
      await fetch(`${API_BASE}/memory/flush`, { method: 'POST' })
      await fetchContext()
      await fetchInfo()
    } catch {
      /* offline */
    }
  }

  useEffect(() => {
    fetchContext()
    fetchEpisodic()
    fetchInfo()
    const t1 = setInterval(fetchContext, 3000)
    const t2 = setInterval(fetchInfo, 5000)
    const t3 = setInterval(fetchEpisodic, 10000)
    return () => {
      clearInterval(t1)
      clearInterval(t2)
      clearInterval(t3)
    }
  }, [fetchContext, fetchEpisodic, fetchInfo])

  const workingEntries = Object.entries(working)

  return (
    <div className="memory-panel">
      <header className="memory-header">
        <span className="live-dot" aria-hidden />
        MEMORY BUS
      </header>

      <section className="memory-section">
        <h3 className="memory-section-title">WORKING MEMORY</h3>
        {workingEntries.length === 0 ? (
          <p className="memory-empty">No active session context</p>
        ) : (
          <ul className="memory-list">
            {workingEntries.map(([key, value]) => (
              <li key={key} className="memory-item">
                <span className="memory-key">{key}</span>
                <span className="memory-value">{String(value)}</span>
              </li>
            ))}
          </ul>
        )}
      </section>

      <section className="memory-section">
        <h3 className="memory-section-title">RECENT ACTIVITY</h3>
        {episodic.length === 0 ? (
          <p className="memory-empty">No activity recorded yet</p>
        ) : (
          <ul className="memory-list">
            {episodic.map((item) => (
              <li key={item.id} className="memory-item memory-item--episodic">
                <span className="memory-time">{formatRelative(item.written_at)}</span>
                <span className="memory-event">{item.content}</span>
              </li>
            ))}
          </ul>
        )}
      </section>

      <footer className="memory-footer">
        <p className="memory-stats">
          {info.working_memory_keys} working keys · uptime {info.uptime_seconds}s
        </p>
        <button type="button" className="btn btn--ghost btn--small" onClick={handleFlush}>
          Clear Session
        </button>
      </footer>
    </div>
  )
}
