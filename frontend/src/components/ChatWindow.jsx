import { useState, useRef, useEffect } from 'react'
import MessageBubble from './MessageBubble'

const AI_DISPLAY = {
  ollama: 'Ollama',
  claude: 'Claude',
  gpt4: 'GPT-4',
  gemini: 'Gemini',
  groq: 'Groq',
  cohere: 'Cohere',
}

export default function ChatWindow({ messages, loading, selectedAI, onSendMessage }) {
  const [input, setInput] = useState('')
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  const handleSubmit = (e) => {
    e.preventDefault()
    const text = input.trim()
    if (!text || loading) return
    setInput('')
    onSendMessage(text)
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  const aiLabel = AI_DISPLAY[selectedAI] || selectedAI

  return (
    <div className="chat-window">
      <div className="chat-thread">
        {messages.length === 0 ? (
          <div className="chat-empty">
            <h1 className="chat-empty-title">AI MEMORY BUS</h1>
            <p className="chat-empty-sub">Your AI tools share one memory</p>
            <ul className="chat-empty-features">
              <li>◆ Memory persists across sessions</li>
              <li>◆ All AIs share the same context</li>
              <li>◆ What one AI learns, all know</li>
            </ul>
          </div>
        ) : (
          messages.map((msg, i) => <MessageBubble key={i} message={msg} />)
        )}
        {loading && (
          <div className="chat-loading">
            <span className="loading-dots">
              <span />
              <span />
              <span />
            </span>
          </div>
        )}
        <div ref={bottomRef} />
      </div>
      <form className="chat-input-row" onSubmit={handleSubmit}>
        <input
          type="text"
          className="chat-input"
          placeholder="Message the memory bus..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={loading}
        />
        <button type="submit" className="btn btn--primary" disabled={loading || !input.trim()}>
          Send
        </button>
        <span className="chat-ai-indicator">{aiLabel}</span>
      </form>
    </div>
  )
}
