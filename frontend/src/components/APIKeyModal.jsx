import { useState } from 'react'

const AI_LABELS = {
  claude: 'Claude',
  gpt4: 'GPT-4',
  gemini: 'Gemini',
  groq: 'Groq',
  cohere: 'Cohere',
}

const KEY_URLS = {
  claude: { url: 'https://console.anthropic.com', label: 'console.anthropic.com' },
  gpt4: { url: 'https://platform.openai.com/api-keys', label: 'platform.openai.com/api-keys' },
  gemini: { url: 'https://aistudio.google.com', label: 'aistudio.google.com' },
  groq: {
    url: 'https://console.groq.com/keys',
    label: 'console.groq.com/keys',
    note: '(free, no credit card)',
  },
  cohere: { url: 'https://dashboard.cohere.com', label: 'dashboard.cohere.com' },
}

export default function APIKeyModal({ targetAI, onSave, onClose }) {
  const [key, setKey] = useState('')
  const label = AI_LABELS[targetAI] || targetAI
  const linkInfo = KEY_URLS[targetAI] || { url: '#', label: '' }

  const handleSave = () => {
    if (key.trim()) {
      localStorage.setItem(`ai_keys_${targetAI}`, key.trim())
      onSave(targetAI, key.trim())
    }
  }

  return (
    <div className="modal-overlay" onClick={onClose} role="presentation">
      <div
        className="modal-sheet"
        onClick={(e) => e.stopPropagation()}
        role="dialog"
        aria-labelledby="modal-title"
      >
        <h2 id="modal-title" className="modal-title">
          Configure {label}
        </h2>
        <p className="modal-subtitle">Get your free API key at:</p>
        <a
          href={linkInfo.url}
          target="_blank"
          rel="noopener noreferrer"
          className="modal-link"
        >
          {linkInfo.label}
          {linkInfo.note && <span className="modal-link-note"> {linkInfo.note}</span>}
        </a>
        <input
          type="password"
          className="modal-input"
          placeholder="Paste your API key here"
          value={key}
          onChange={(e) => setKey(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSave()}
        />
        <div className="modal-actions">
          <button type="button" className="btn btn--ghost" onClick={onClose}>
            Cancel
          </button>
          <button type="button" className="btn btn--primary" onClick={handleSave}>
            Save &amp; Use
          </button>
        </div>
      </div>
    </div>
  )
}
