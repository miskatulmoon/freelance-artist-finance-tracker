import type { FormEvent } from 'react'
import { useEffect, useRef, useState } from 'react'
import { api } from '../api'

interface Message {
  role: 'user' | 'assistant'
  text: string
}

const SUGGESTIONS = [
  'Which income source earned me the most?',
  'What is my effective hourly rate and is it healthy?',
  'How much have I paid in platform fees?',
  'What is my projected balance in 30 days?',
]

export function Chat() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      text: 'Ask me anything about your finances — I read your actual numbers right now, so questions like "what did I clear on Etsy after fees?" get concrete answers.',
    },
  ])
  const [input, setInput] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const logRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    logRef.current?.scrollTo({ top: logRef.current.scrollHeight })
  }, [messages])

  const ask = async (question: string) => {
    if (!question.trim() || busy) return
    setBusy(true)
    setError('')
    setMessages((m) => [...m, { role: 'user', text: question }])
    setInput('')
    try {
      const res = await api.chat(question)
      setMessages((m) => [...m, { role: 'assistant', text: res.answer }])
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to get an answer')
    } finally {
      setBusy(false)
    }
  }

  const onSubmit = (e: FormEvent) => {
    e.preventDefault()
    void ask(input)
  }

  return (
    <div className="stack">
      <div className="card">
        <h3>Chat with your finances</h3>
        <div className="chat-log" ref={logRef}>
          {messages.map((m, i) => (
            <div key={i} className={`chat-msg ${m.role}`}>
              {m.text}
            </div>
          ))}
          {busy && <div className="chat-msg assistant loading">Reading your numbers…</div>}
        </div>
        {error && <p className="error">{error}</p>}
        <div className="text-dim" style={{ fontSize: 12, marginTop: 12 }}>
          Try:
        </div>
        <div className="form-row" style={{ marginTop: 6 }}>
          {SUGGESTIONS.map((s) => (
            <button key={s} type="button" className="ghost" onClick={() => void ask(s)} disabled={busy} style={{ fontSize: 12.5 }}>
              {s}
            </button>
          ))}
        </div>
        <form className="chat-input-row" onSubmit={onSubmit}>
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="e.g. How much did Etsy make after fees?"
            disabled={busy}
          />
          <button className="btn" disabled={busy || !input.trim()}>
            Ask
          </button>
        </form>
      </div>
    </div>
  )
}