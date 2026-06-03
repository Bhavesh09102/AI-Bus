import { useState } from 'react'

const AI_DISPLAY = {
  ollama: 'Ollama',
  claude: 'Claude',
  gpt4: 'GPT-4',
  gemini: 'Gemini',
  groq: 'Groq',
  cohere: 'Cohere',
}

export default function MessageBubble({ message }) {
  const [expanded, setExpanded] = useState(false)
  const { role, content, ai_used, context_injected, memories_used } = message

  if (role === 'user') {
    return (
      <div className="message-row message-row--user">
        <div className="bubble bubble--user">{content}</div>
      </div>
    )
  }

  if (role === 'error') {
    return (
      <div className="message-row message-row--ai">
        <div className="bubble bubble--error">{content}</div>
      </div>
    )
  }

  const aiName = AI_DISPLAY[ai_used] || ai_used || 'AI'
  const memCount = memories_used ?? 0
  const hasContext = context_injected && context_injected.trim().length > 0

  return (
    <div className="message-row message-row--ai">
      <button
        type="button"
        className="message-meta"
        onClick={() => hasContext && setExpanded(!expanded)}
        disabled={!hasContext}
      >
        {aiName} · {memCount} memories used
        {hasContext && <span className="message-meta-chevron">{expanded ? ' ▾' : ' ▸'}</span>}
      </button>
      <div className="bubble bubble--ai">{content}</div>
      {expanded && hasContext && (
        <div className="context-panel">
          <div className="context-panel-label">Injected context</div>
          <pre className="context-panel-body">{context_injected}</pre>
        </div>
      )}
    </div>
  )
}
