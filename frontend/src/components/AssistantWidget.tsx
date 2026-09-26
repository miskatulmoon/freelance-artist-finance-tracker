import type { FormEvent } from 'react'
import { useEffect, useRef, useState } from 'react'
import { api } from '../api'
import { NibIcon } from './icons'

interface Message {
  role: 'user' | 'assistant'
  text: string
}

const WELCOME = 'Ask one question about your ledger. I will answer from your real numbers.'

const SUGGESTIONS = ['How is my studio doing?', 'What is my hourly rate?', 'How much did Etsy make after fees?']

export function AssistantWidget() {
  const [open, setOpen] = useState(false)
  const [messages, setMessages] = useState<Message[]>([{ role: 'assistant', text: WELCOME }])
  const [input, setInput] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const logRef = useRef<HTMLDivElement>(null)
  const abortRef = useRef<AbortController | null>(null)

  useEffect(() => {
    if (open) logRef.current?.scrollTo({ top: logRef.current.scrollHeight })
  }, [messages, open])

  useEffect(() => () => abortRef.current?.abort(), [])

  const updateLastAssistant = (fn: (text: string) => string) =>
    setMessages((m) => {
      const next = [...m]
      const last = next[next.length - 1]
      if (last?.role !== 'assistant') return m
      next[next.length - 1] = { ...last, text: fn(last.text) }
      return next
    })

  const ask = async (question?: string) => {
    const q = (question ?? input).trim()
    if (!q || busy) return
    const controller = new AbortController()
    abortRef.current = controller
    setBusy(true)
    setError('')
    setMessages((m) => [...m, { role: 'user', text: q }])
    setInput('')
    try {
      let started = false
      await api.streamChat(
        q,
        (delta) => {
          if (!started) {
            started = true
            setMessages((m) => [...m, { role: 'assistant', text: delta }])
          } else {
            updateLastAssistant((t) => t + delta)
          }
        },
        controller.signal,
      )
    } catch (e) {
      if (!controller.signal.aborted) {
        setError(e instanceof Error ? e.message : 'Failed to get an answer')
      }
    } finally {
      abortRef.current = null
      setBusy(false)
    }
  }

  const onSubmit = (e: FormEvent) => {
    e.preventDefault()
    void ask()
  }

  const stop = () => abortRef.current?.abort()

  const toggle = () => setOpen((v) => !v)

  return (
    <>
      <button
        type="button"
        className="a-fab"
        aria-label={open ? 'Minimize the assistant' : 'Ask your assistant'}
        aria-expanded={open}
        onClick={toggle}
      >
        <NibIcon />
      </button>

      {open && (
        <section className="a-panel" aria-label="Assistant">
          <header className="a-head">
            <div>
              <h2 className="a-title">Ask about your ledger</h2>
              <p className="a-subtitle">Plain answers from your real numbers.</p>
            </div>
            <button type="button" className="a-min" aria-label="Minimize the assistant" onClick={toggle}>
              −
            </button>
          </header>

          <div className="chat-log a-log" ref={logRef} role="log" aria-live="polite">
            {messages.map((m, i) => (
              <div key={i} className={`chat-msg ${m.role}${m.role === 'assistant' ? ' note-reveal' : ''}`}>
                {m.text}
              </div>
            ))}
            {busy && <div className="a-status">Thinking…</div>}
          </div>

          {error && <p className="error a-error">{error}</p>}

          <footer className="a-foot">
            <div className="a-suggestions">
              {SUGGESTIONS.map((s) => (
                <button key={s} type="button" className="ghost" onClick={() => void ask(s)} disabled={busy}>
                  {s}
                </button>
              ))}
            </div>
            <form className="chat-input-row" onSubmit={onSubmit}>
              <input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Type your question"
                disabled={busy}
                aria-label="Ask the assistant a question"
              />
              {busy ? (
                <button type="button" className="btn a-stop" onClick={stop} aria-label="Stop the assistant response">
                  Stop
                </button>
              ) : (
                <button className="btn" disabled={!input.trim()}>
                  Ask
                </button>
              )}
            </form>
          </footer>
        </section>
      )}
    </>
  )
}