import { useState, useRef, useEffect } from 'react'
import { sendChatMessage } from '../../services/api'

function MessageBubble({ message }) {
  const isUser = message.role === 'user'

  return (
    <div className={`flex gap-3 ${isUser ? 'justify-end' : 'justify-start'}`}>
      {!isUser && (
        <div 
          className="flex items-center justify-center text-sm flex-shrink-0 mt-1 rounded-full"
          style={{
            width: '32px',
            height: '32px',
            border: '2px solid var(--gold)',
            background: 'var(--surface)'
          }}
        >
          ♟
          <div 
            className="absolute rounded-full"
            style={{
              width: '8px',
              height: '8px',
              background: 'var(--green)',
              bottom: '0',
              right: '0',
              border: '2px solid var(--obsidian)'
            }}
          />
        </div>
      )}
      <div 
        className="max-w-[80%] px-4 py-3 font-body text-sm"
        style={{
          background: isUser ? 'rgba(196,158,66,0.10)' : 'var(--card)',
          border: `1px solid ${isUser ? 'var(--border-hi)' : 'var(--border)'}`,
          borderRadius: isUser ? '12px 4px 12px 12px' : '4px 12px 12px 12px',
          color: 'rgba(237,228,204,0.88)',
          lineHeight: 1.65
        }}
      >
        {message.content.split('\n').map((line, i) => (
          <p key={i} className={line.startsWith('#')
            ? 'font-bold mb-1'
            : line.startsWith('**') || line.startsWith('-')
              ? 'mb-0.5'
              : 'mb-0.5'}
             style={{ color: 'rgba(237,228,204,0.88)' }}
          >
            {line.replace(/#{1,3}\s/, '').replace(/\*\*/g, '')}
          </p>
        ))}
      </div>
      {isUser && (
        <div 
          className="flex items-center justify-center text-sm flex-shrink-0 mt-1 rounded-full"
          style={{
            width: '32px',
            height: '32px',
            background: 'var(--surface)',
            border: '1px solid var(--border)'
          }}
        >
          👤
        </div>
      )}
    </div>
  )
}

const SUGGESTED_QUESTIONS = [
  "What races are available on Feb 7th?",
  "Which jockeys performed best this week?",
  "Explain how the ML model works",
  "What's a value bet?",
]

export default function ChatPanel({ raceId = null, className = '' }) {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: raceId
        ? "I've loaded the race data. Ask me anything about this race - runners, odds, predictions, or betting strategy!"
        : "Hi! I'm your AI racing expert. I have access to race cards, ML predictions, and historical data. What would you like to know?"
    }
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef(null)

  useEffect(() => {
    // Only scroll within the chat container, not the entire page
    if (bottomRef.current) {
      const container = bottomRef.current.parentElement
      if (container) {
        container.scrollTop = container.scrollHeight
      }
    }
  }, [messages])

  const sendMessage = async (text) => {
    const messageText = text || input.trim()
    if (!messageText || loading) return

    const userMessage = { role: 'user', content: messageText }
    const newMessages = [...messages, userMessage]
    setMessages(newMessages)
    setInput('')
    setLoading(true)

    try {
      // Build history (exclude first greeting)
      const history = newMessages.slice(1).map(m => ({
        role: m.role,
        content: m.content
      }))

      const res = await sendChatMessage(messageText, history, raceId)
      const responseText = res.data.response

      setMessages(prev => [...prev, {
        role: 'assistant',
        content: responseText
      }])
    } catch {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: "Sorry, I'm having trouble connecting right now. Make sure the MCP server is running on port 5002."
      }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div 
      className={`flex flex-col overflow-hidden ${className}`}
      style={{
        background: 'var(--obsidian)',
        border: '1px solid rgba(196,158,66,0.12)',
        borderRadius: '16px',
      }}
    >
      {/* Top Border Glow */}
      <div style={{
        height: '2px',
        background: 'linear-gradient(90deg, transparent, var(--gold), transparent)',
        opacity: 0.3
      }} />

      {/* Header */}
      <div 
        className="px-4 py-3 flex items-center gap-3"
        style={{ borderBottom: '1px solid var(--border)' }}
      >
        {/* Avatar with online dot */}
        <div className="relative">
          <div 
            className="flex items-center justify-center rounded-full"
            style={{
              width: '36px',
              height: '36px',
              border: '2px solid var(--gold)',
              background: 'var(--surface)'
            }}
          >
            ♟
          </div>
          <div 
            className="absolute rounded-full"
            style={{
              width: '10px',
              height: '10px',
              background: 'var(--green)',
              bottom: '0',
              right: '0',
              border: '2px solid var(--obsidian)'
            }}
          />
        </div>
        
        <div className="flex-1">
          <div className="font-display text-base" style={{ color: 'var(--cream)' }}>
            AI Racing Expert
          </div>
          <div className="font-mono text-[8px]" style={{ color: 'var(--muted)' }}>
            Online · {messages.length - 1} messages
          </div>
        </div>

        <div 
          className="font-mono text-[8px] rounded-full px-3 py-1"
          style={{
            background: 'rgba(255,255,255,0.03)',
            border: '1px solid var(--border)',
            color: 'var(--muted)'
          }}
        >
          Claude + RAG · ML Active
        </div>
      </div>

      {/* Messages */}
      <div 
        className="flex-1 overflow-y-auto p-4 space-y-4"
        style={{ minHeight: '300px', maxHeight: '500px' }}
      >
        {messages.map((msg, i) => (
          <MessageBubble key={i} message={msg} />
        ))}

        {loading && (
          <div className="flex gap-3 justify-start">
            <div 
              className="flex items-center justify-center text-sm flex-shrink-0 rounded-full"
              style={{
                width: '32px',
                height: '32px',
                border: '2px solid var(--gold)',
                background: 'var(--surface)'
              }}
            >
              ♟
            </div>
            <div 
              className="rounded-2xl px-4 py-3"
              style={{
                background: 'var(--card)',
                borderRadius: '4px 12px 12px 12px'
              }}
            >
              <div className="flex gap-1 items-center h-5">
                <div className="w-2 h-2 rounded-full animate-bounce" style={{ background: 'var(--slate)', animationDelay: '0ms' }} />
                <div className="w-2 h-2 rounded-full animate-bounce" style={{ background: 'var(--slate)', animationDelay: '150ms' }} />
                <div className="w-2 h-2 rounded-full animate-bounce" style={{ background: 'var(--slate)', animationDelay: '300ms' }} />
              </div>
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* Suggested Questions (show only at start) */}
      {messages.length === 1 && !raceId && (
        <div className="px-4 pb-3 flex flex-wrap gap-2">
          {SUGGESTED_QUESTIONS.map(q => (
            <button
              key={q}
              onClick={() => sendMessage(q)}
              className="font-mono text-[9px] px-3 py-1.5 rounded-full transition-all"
              style={{
                background: 'var(--card)',
                border: '1px solid var(--border)',
                color: 'var(--slate)'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.borderColor = 'var(--border-hi)'
                e.currentTarget.style.color = 'var(--gold)'
                e.currentTarget.style.background = 'var(--gold-glow)'
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.borderColor = 'var(--border)'
                e.currentTarget.style.color = 'var(--slate)'
                e.currentTarget.style.background = 'var(--card)'
              }}
            >
              {q}
            </button>
          ))}
        </div>
      )}

      {/* Input */}
      <div 
        className="p-4 flex gap-2"
        style={{ 
          background: 'var(--surface)',
          borderTop: '1px solid var(--border)'
        }}
      >
        <input
          type="text"
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && !e.shiftKey && sendMessage()}
          placeholder={raceId
            ? "Ask about this race..."
            : "Ask about races, predictions, strategy..."}
          disabled={loading}
          className="flex-1 px-3 py-2 text-sm rounded-lg transition-all font-body"
          style={{
            background: 'var(--card)',
            border: '1px solid var(--border)',
            color: 'var(--cream)',
            outline: 'none'
          }}
          onFocus={(e) => {
            e.currentTarget.style.borderColor = 'var(--border-hi)'
          }}
          onBlur={(e) => {
            e.currentTarget.style.borderColor = 'var(--border)'
          }}
        />
        <button
          onClick={() => sendMessage()}
          disabled={loading || !input.trim()}
          className="px-4 py-2 rounded-lg text-sm font-medium font-mono transition-colors"
          style={{
            background: loading || !input.trim() ? 'var(--muted)' : 'linear-gradient(135deg, var(--gold), #A8852E)',
            color: 'var(--obsidian)',
            border: 'none',
            cursor: loading || !input.trim() ? 'not-allowed' : 'pointer',
            opacity: loading || !input.trim() ? 0.4 : 1
          }}
        >
          Send
        </button>
      </div>
    </div>
  )
}