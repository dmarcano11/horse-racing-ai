import ChatPanel from '../components/chat/ChatPanel'
import GoldRule from '../components/ui/GoldRule'

export default function ChatPage() {
  return (
    <div className="min-h-screen" style={{ background: 'var(--deep)', paddingTop: '20px' }}>
      <div className="max-w-4xl mx-auto px-4">
        <div className="font-mono text-[9px] tracking-[0.35em] uppercase mb-3" style={{ color: 'rgba(196,158,66,0.6)' }}>
          Powered by Claude + RAG
        </div>
        <h1 className="font-display text-4xl mb-2" style={{ color: 'var(--cream)' }}>
          AI Racing Expert
        </h1>
        <p className="font-mono text-[10px] mb-6" style={{ color: 'var(--muted)' }}>
          Ask about today's races, runners, predictions, and betting strategy
        </p>
        <GoldRule />
        <ChatPanel className="h-[680px]" />
      </div>
    </div>
  )
}