import { useState, useCallback } from 'react'

const API_BASE = 'http://localhost:5000'

export function useChat() {
  const [messages, setMessages] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const sendMessage = useCallback(async (userMessage, selectedAI, apiKeys) => {
    setMessages((prev) => [...prev, { role: 'user', content: userMessage }])
    setLoading(true)
    setError(null)

    const api_key = apiKeys[selectedAI] || ''

    try {
      const res = await fetch(`${API_BASE}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: userMessage,
          ai: selectedAI,
          api_key,
          model: 'llama3',
        }),
      })

      const data = await res.json()

      if (!res.ok) {
        setMessages((prev) => [
          ...prev,
          { role: 'error', content: data.error || 'Request failed' },
        ])
        setError(data.error)
        return
      }

      const breakdown = data.memory_breakdown || {}
      const memoriesUsed =
        data.memories_used ??
        (breakdown.working || 0) + (breakdown.episodic || 0) + (breakdown.semantic || 0)

      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: data.response,
          ai_used: data.ai_used,
          context_injected: data.context_injected,
          memories_used: memoriesUsed,
          memory_breakdown: breakdown,
        },
      ])
    } catch (err) {
      const msg = err.message || 'Network error — is the backend running?'
      setMessages((prev) => [...prev, { role: 'error', content: msg }])
      setError(msg)
    } finally {
      setLoading(false)
    }
  }, [])

  return { messages, loading, error, sendMessage }
}
