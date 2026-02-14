import ChatPanel from '../components/chat/ChatPanel'

export default function ChatPage() {
  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">AI Racing Expert</h1>
        <p className="text-slate-400 text-sm mt-1">
          Ask anything about races, predictions, betting strategy, or historical data
        </p>
      </div>
      <ChatPanel className="h-full" />
    </div>
  )
}