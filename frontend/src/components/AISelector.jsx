const AIS = [
  { id: 'ollama', name: 'Ollama', icon: '🦙', badge: 'LOCAL · FREE', local: true },
  { id: 'claude', name: 'Claude', icon: '●', badge: 'Anthropic' },
  { id: 'gpt4', name: 'GPT-4', icon: '◆', badge: 'OpenAI' },
  { id: 'gemini', name: 'Gemini', icon: '◈', badge: 'Google' },
  { id: 'groq', name: 'Groq', icon: '⚡', badge: 'FREE API' },
  { id: 'cohere', name: 'Cohere', icon: '◉', badge: 'Cohere' },
]

export default function AISelector({ selectedAI, apiKeys, onSelectAI, onRequestKey }) {
  const isUnlocked = (ai) => ai.local || Boolean(apiKeys[ai.id])
  const isSelected = (id) => selectedAI === id

  const handleClick = (ai) => {
    if (isUnlocked(ai)) {
      onSelectAI(ai.id)
    } else {
      onRequestKey(ai.id)
    }
  }

  return (
    <div className="ai-selector">
      <h2 className="ai-selector-title">AI PROVIDERS</h2>
      <div className="ai-grid">
        {AIS.map((ai) => {
          const unlocked = isUnlocked(ai)
          const selected = isSelected(ai.id)
          return (
            <button
              key={ai.id}
              type="button"
              className={`ai-card ${selected ? 'ai-card--selected' : ''} ${!unlocked ? 'ai-card--locked' : ''}`}
              onClick={() => handleClick(ai)}
            >
              <span className="ai-card-icon">{ai.icon}</span>
              <span className="ai-card-name">{ai.name}</span>
              <span className="ai-card-badge">
                {ai.id === 'groq' ? 'NO CREDIT CARD' : ai.badge}
              </span>
              {ai.local ? (
                <span className="ai-card-status">NO KEY NEEDED</span>
              ) : selected ? null : unlocked ? (
                <span className="ai-card-status ai-card-status--ok">✓</span>
              ) : (
                <span className="ai-card-status">🔒</span>
              )}
            </button>
          )
        })}
      </div>
    </div>
  )
}
