import { useState, useRef, useEffect } from 'react'
import { sendChatMessage } from '../../services/api'

function MessageBubble({ message }) {
  const isUser = message.role === 'user'

  return (
    <div className={`flex gap-3 ${isUser ? 'justify-end' : 'justify-start'}`}>
      {!isUser && (
        <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center
                        justify-center text-sm flex-shrink-0 mt-1">
          🏇
        </div>
      )}
      <div className={`max-w-[80%] rounded-2xl px-4 py-3 text-sm leading-relaxed
                      ${isUser
                        ? 'bg-blue-600 text-white rounded-tr-sm'
                        : 'bg-slate-700 text-slate-100 rounded-tl-sm'}`}>
        {/* Render markdown-style bold */}
        {message.content.split('\n').map((line, i) => (
          <p key={i} className={line.startsWith('#')
            ? 'font-bold text-white mb-1'
            : line.startsWith('**') || line.startsWith('-')
              ? 'text-slate-200 mb-0.5'
              : 'mb-0.5'}>
            {line.replace(/#{1,3}\s/, '').replace(/\*\*/g, '')}
          </p>
        ))}
      </div>
      {isUser && (
        <div className="w-8 h-8 rounded-full bg-slate-600 flex items-center
                        justify-center text-sm flex-shrink-0 mt-1">
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
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
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
    } catch (err) {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: "Sorry, I'm having trouble connecting right now. Make sure the MCP server is running on port 5002."
      }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className={`flex flex-col bg-slate-800 rounded-xl border
                    border-slate-700 overflow-hidden ${className}`}>

      {/* Header */}
      <div className="px-4 py-3 border-b border-slate-700 flex items-center gap-2">
        <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
        <span className="text-sm font-medium text-white">AI Racing Expert</span>
        <span className="text-xs text-slate-400 ml-auto">
          Powered by Claude + RAG
        </span>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 min-h-[300px]
                      max-h-[500px]">
        {messages.map((msg, i) => (
          <MessageBubble key={i} message={msg} />
        ))}

        {loading && (
          <div className="flex gap-3 justify-start">
            <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center
                            justify-center text-sm flex-shrink-0">
              🏇
            </div>
            <div className="bg-slate-700 rounded-2xl rounded-tl-sm px-4 py-3">
              <div className="flex gap-1 items-center h-5">
                <div className="w-2 h-2 rounded-full bg-slate-400
                                animate-bounce [animation-delay:0ms]" />
                <div className="w-2 h-2 rounded-full bg-slate-400
                                animate-bounce [animation-delay:150ms]" />
                <div className="w-2 h-2 rounded-full bg-slate-400
                                animate-bounce [animation-delay:300ms]" />
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
              className="text-xs px-3 py-1.5 rounded-full bg-slate-700
                         hover:bg-slate-600 text-slate-300 hover:text-white
                         transition-colors border border-slate-600"
            >
              {q}
            </button>
          ))}
        </div>
      )}

      {/* Input */}
      <div className="p-3 border-t border-slate-700 flex gap-2">
        <input
          type="text"
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && !e.shiftKey && sendMessage()}
          placeholder={raceId
            ? "Ask about this race..."
            : "Ask about races, predictions, strategy..."}
          disabled={loading}
          className="flex-1 bg-slate-700 border border-slate-600 rounded-lg
                     px-3 py-2 text-sm text-white placeholder-slate-400
                     focus:outline-none focus:border-blue-500
                     disabled:opacity-50"
        />
        <button
          onClick={() => sendMessage()}
          disabled={loading || !input.trim()}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-500 disabled:opacity-40
                     disabled:cursor-not-allowed rounded-lg text-white text-sm
                     font-medium transition-colors"
        >
          Send
        </button>
      </div>
    </div>
  )
}