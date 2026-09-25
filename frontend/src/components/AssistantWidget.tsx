import type { FormEvent } from 'react'
import { useEffect, useRef, useState } from 'react'
import { api } from '../api'
import { NibIcon } from './icons'

interface Message {
  role: 'user' | 'assistant'
  text: string
}

const WELCOME =
  "I'm the extra pencil on your desk. Ask me about your ledger — what Etsy cleared after fees, your effective rate, or where the next 30 days are heading."

export function AssistantWidget() {
  const [open, setOpen] = useState(false)
  const [messages, setMessages] = useState<Message[]>([{ role: 'assistant', text: WELCOME }])
  const [input, setInput] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const logRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (open) logRef.current?.scrollTo({ top: logRef.current.scrollHeight })
  }, [messages, open])

  const updateLastAssistant = (fn: (text: string) => string) =>
    setMessages((m) => {
      const next = [...m]
      const last = next[next.length - 1]
      if (last?.role !== 'assistant') return m
      next[next.length - 1] = { ...last, text: fn(last.text) }
      return next
    })

  const dropEmptyAssistant = () =>
    setMessages((m) => {
      const last = m[m.length - 1]
      return last?.role === 'assistant' && last.text === '' ? m.slice(0, -1) : m
    })

  const ask = async (question?: string) => {
    const q = (question ?? input).trim()
    if (!q || busy) return
    setBusy(true)
    setError('')
    setMessages((m) => [...m, { role: 'user', text: q }, { role: 'assistant', text: '' }])
    setInput('')
    try {
      await api.streamChat(q, (delta) => updateLastAssistant((t) => t + delta))
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to get an answer')
      dropEmptyAssistant()
    } finally {
      setBusy(false)
    }
  }

  const readTheStudio = async () => {
    if (busy) return
    setBusy(true)
    setError('')
    setMessages((m) => [...m, { role: 'user', text: 'Read me the state of the studio.' }, { role: 'assistant', text: '' }])
    try {
      const [i, c] = await Promise.all([api.getInsights(), api.getRadarNarrative()])
      updateLastAssistant(() => `${i.insights}\n\n${c.narrative}`)
    } catch (e) {
      setError(e instanceof Error ? e.message : "Couldn't pencil the note")
      dropEmptyAssistant()
    } finally {
      setBusy(false)
    }
  }

  const onSubmit = (e: FormEvent) => {
    e.preventDefault()
    void ask()
  }

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
            <h2 className="a-title">
              A note from
              <br />
              your assistant
            </h2>
            <button type="button" className="a-min" aria-label="Minimize the assistant" onClick={toggle}>
              −
            </button>
          </header>

          <div className="chat-log a-log" ref={logRef} role="log" aria-live="polite">
            {messages.map((m, i) => (
              <div
                key={i}
                className={`chat-msg ${m.role}${m.role === 'assistant' ? ' note-reveal' : ''}`}
                aria-busy={busy && i === messages.length - 1 && m.role === 'assistant'}
              >
                {m.text}
              </div>
            ))}
            {busy && messages[messages.length - 1]?.role === 'assistant' && messages[messages.length - 1].text === '' && (
              <div className="chat-msg assistant loading">Penciling…</div>
            )}
          </div>

          {error && <p className="error a-error">{error}</p>}

          <footer className="a-foot">
            <button
              type="button"
              className="ghost a-note-btn"
              onClick={() => void readTheStudio()}
              disabled={busy}
            >
              Read me the state of the studio
            </button>
            <div className="text-dim a-hint">Try asking:</div>
            <div className="a-suggestions">
              {[
                'Which income source earned me the most?',
                'What is my effective hourly rate and is it healthy?',
                'How much have I paid in platform fees?',
              ].map((s) => (
                <button key={s} type="button" className="ghost" onClick={() => void ask(s)} disabled={busy}>
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
                aria-label="Ask the assistant a question"
              />
              <button className="btn" disabled={busy || !input.trim()}>
                Ask
              </button>
            </form>
          </footer>
        </section>
      )}
    </>
  )
}