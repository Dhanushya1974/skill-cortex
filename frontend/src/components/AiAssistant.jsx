import { useEffect, useRef, useState } from "react"
import { useAuth } from "../context/AuthContext"
import { api } from "../services/api"

export default function AiAssistant() {
  const { token } = useAuth()
  const [open, setOpen] = useState(false)
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState("")
  const [sending, setSending] = useState(false)
  const [error, setError] = useState("")
  const scrollRef = useRef(null)

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight })
  }, [messages, open])

  async function handleSend(e) {
    e.preventDefault()
    const text = input.trim()
    if (!text || sending) return

    setError("")
    setInput("")
    const history = messages
    setMessages((m) => [...m, { role: "user", content: text }])
    setSending(true)
    try {
      const { reply } = await api.chatWithAssistant(text, history, token)
      setMessages((m) => [...m, { role: "assistant", content: reply }])
    } catch (err) {
      setError(err.message)
    } finally {
      setSending(false)
    }
  }

  return (
    <div className="fixed left-4 top-4 z-50 md:top-20">
      <button
        onClick={() => setOpen((o) => !o)}
        className="flex h-12 w-12 items-center justify-center rounded-full bg-primary text-lg text-white shadow-lg transition hover:bg-primary-dark"
        aria-label="Toggle Skill Cortex AI assistant"
      >
        {open ? "✕" : "🧠"}
      </button>

      {open && (
        <div className="mt-3 flex h-[28rem] w-80 flex-col overflow-hidden rounded-2xl border border-black/10 bg-white shadow-2xl">
          <div className="border-b border-black/5 bg-ink px-4 py-3">
            <p className="text-sm font-semibold text-white">Skill Cortex Assistant</p>
            <p className="text-xs text-white/60">Ask about your bookings, payments, or webinars</p>
          </div>

          <div ref={scrollRef} className="flex-1 space-y-3 overflow-y-auto px-4 py-3">
            {messages.length === 0 && (
              <p className="text-sm text-ink/50">
                Hi! I can help with your bookings, payments, and how Skill Cortex works. What do you need?
              </p>
            )}
            {messages.map((m, i) => (
              <div
                key={i}
                className={`max-w-[85%] whitespace-pre-wrap rounded-xl px-3 py-2 text-sm ${
                  m.role === "user" ? "ml-auto bg-primary text-white" : "bg-surface text-ink"
                }`}
              >
                {m.content}
              </div>
            ))}
            {sending && (
              <div className="max-w-[85%] rounded-xl bg-surface px-3 py-2 text-sm text-ink/50">Thinking…</div>
            )}
            {error && <p className="text-xs text-red-600">{error}</p>}
          </div>

          <form onSubmit={handleSend} className="flex items-center gap-2 border-t border-black/5 p-3">
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask something..."
              className="flex-1 rounded-lg border border-black/10 px-3 py-2 text-sm outline-none focus:border-primary"
            />
            <button
              type="submit"
              disabled={sending || !input.trim()}
              className="rounded-lg bg-primary px-3 py-2 text-sm font-semibold text-white transition hover:bg-primary-dark disabled:opacity-50"
            >
              Send
            </button>
          </form>
        </div>
      )}
    </div>
  )
}
