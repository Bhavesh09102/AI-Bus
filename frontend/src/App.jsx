import { useState, useCallback } from 'react'
import AISelector from './components/AISelector'
import APIKeyModal from './components/APIKeyModal'
import ChatWindow from './components/ChatWindow'
import MemoryPanel from './components/MemoryPanel'
import { useChat } from './hooks/useChat'

const AI_NAMES = ['ollama', 'claude', 'gpt4', 'gemini', 'groq', 'cohere']

function loadApiKeys() {
  const keys = {}
  AI_NAMES.forEach((ai) => {
    const stored = localStorage.getItem(`ai_keys_${ai}`)
    if (stored) keys[ai] = stored
  })
  return keys
}

export default function App() {
  const [selectedAI, setSelectedAI] = useState('ollama')
  const [apiKeys, setApiKeys] = useState(loadApiKeys)
  const [showKeyModal, setShowKeyModal] = useState(false)
  const [modalTargetAI, setModalTargetAI] = useState('claude')

  const { messages, loading, sendMessage } = useChat()

  const handleSelectAI = useCallback((ai) => {
    setSelectedAI(ai)
  }, [])

  const handleRequestKey = useCallback((ai) => {
    setModalTargetAI(ai)
    setShowKeyModal(true)
  }, [])

  const handleSaveKey = useCallback((ai, key) => {
    localStorage.setItem(`ai_keys_${ai}`, key)
    setApiKeys((prev) => ({ ...prev, [ai]: key }))
    setSelectedAI(ai)
    setShowKeyModal(false)
  }, [])

  const handleSendMessage = useCallback(
    (text) => {
      sendMessage(text, selectedAI, apiKeys)
    },
    [sendMessage, selectedAI, apiKeys],
  )

  return (
    <div className="app-layout">
      <aside className="sidebar-left">
        <AISelector
          selectedAI={selectedAI}
          apiKeys={apiKeys}
          onSelectAI={handleSelectAI}
          onRequestKey={handleRequestKey}
        />
      </aside>
      <main className="main-chat">
        <ChatWindow
          messages={messages}
          loading={loading}
          selectedAI={selectedAI}
          onSendMessage={handleSendMessage}
        />
      </main>
      <aside className="sidebar-right">
        <MemoryPanel />
      </aside>
      {showKeyModal && (
        <APIKeyModal
          targetAI={modalTargetAI}
          onSave={handleSaveKey}
          onClose={() => setShowKeyModal(false)}
        />
      )}
    </div>
  )
}
