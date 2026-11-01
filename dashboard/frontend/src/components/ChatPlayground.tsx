import { useState, useRef, useEffect } from 'react'
import { api } from '../utils/api'
import {
  Bot, Send, Loader2, User, Wrench, Key, ChevronDown,
  ChevronRight, AlertCircle, Sparkles, Trash2, Settings,
} from 'lucide-react'

/* ------------------------------------------------------------------ */
/* Types                                                               */
/* ------------------------------------------------------------------ */

interface ContentBlock {
  type: string
  text?: string
  id?: string
  name?: string
  input?: Record<string, any>
  tool_use_id?: string
  content?: string
  is_error?: boolean
}

interface Message {
  role: 'user' | 'assistant'
  content: string | ContentBlock[]
}

interface DisplayItem {
  key: number
  kind: 'user_text' | 'assistant_text' | 'tool_call' | 'tool_result' | 'thinking'
  text?: string
  toolName?: string
  toolInput?: Record<string, any>
  toolId?: string
  isError?: boolean
}

const MODELS = [
  { id: 'claude-opus-4-6', label: 'Claude Opus 4.6' },
  { id: 'claude-opus-4-5', label: 'Claude Opus 4.5' },
]

let _dk = 0

/* ------------------------------------------------------------------ */
/* Component                                                           */
/* ------------------------------------------------------------------ */

export default function ChatPlayground({ challengeId }: { challengeId: number }) {
  const [apiKey, setApiKey] = useState(() => localStorage.getItem('dvmcp_anthropic_key') || '')
  const [model, setModel] = useState(MODELS[0].id)
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [showSettings, setShowSettings] = useState(() => !localStorage.getItem('dvmcp_anthropic_key'))
  const [usage, setUsage] = useState({ input_tokens: 0, output_tokens: 0 })
  const [expandedTools, setExpandedTools] = useState<Record<string, boolean>>({})
  const chatEndRef = useRef<HTMLDivElement>(null)

  // persist key
  useEffect(() => {
    if (apiKey) localStorage.setItem('dvmcp_anthropic_key', apiKey)
    else localStorage.removeItem('dvmcp_anthropic_key')
  }, [apiKey])

  // auto-scroll
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  /* -------- flatten messages for display -------- */
  const displayItems: DisplayItem[] = []
  for (const msg of messages) {
    if (msg.role === 'user' && typeof msg.content === 'string') {
      displayItems.push({ key: ++_dk, kind: 'user_text', text: msg.content })
    } else if (msg.role === 'assistant' && Array.isArray(msg.content)) {
      for (const block of msg.content) {
        if (block.type === 'text' && block.text) {
          displayItems.push({ key: ++_dk, kind: 'assistant_text', text: block.text })
        } else if (block.type === 'tool_use') {
          displayItems.push({
            key: ++_dk,
            kind: 'tool_call',
            toolName: block.name,
            toolInput: block.input,
            toolId: block.id,
          })
        }
      }
    } else if (msg.role === 'user' && Array.isArray(msg.content)) {
      // tool results (auto-generated, not real user messages)
      for (const block of msg.content) {
        if (block.type === 'tool_result') {
          displayItems.push({
            key: ++_dk,
            kind: 'tool_result',
            text: block.content,
            toolId: block.tool_use_id,
            isError: block.is_error,
          })
        }
      }
    }
  }

  /* -------- send -------- */
  const send = async () => {
    const text = input.trim()
    if (!text || !apiKey.trim() || loading) return
    setError('')
    setInput('')

    const userMsg: Message = { role: 'user', content: text }
    const allMessages = [...messages, userMsg]
    setMessages(allMessages)
    setLoading(true)

    try {
      const res = await api.playgroundChat(challengeId, apiKey.trim(), allMessages, model)
      setMessages([...allMessages, ...res.new_messages])
      setUsage((prev) => ({
        input_tokens: prev.input_tokens + (res.usage?.input_tokens || 0),
        output_tokens: prev.output_tokens + (res.usage?.output_tokens || 0),
      }))
    } catch (e: any) {
      setError(e.message || 'Chat request failed')
    } finally {
      setLoading(false)
    }
  }

  const clearChat = () => {
    setMessages([])
    setUsage({ input_tokens: 0, output_tokens: 0 })
    setError('')
  }

  const toggleToolExpand = (id: string) => {
    setExpandedTools((prev) => ({ ...prev, [id]: !prev[id] }))
  }

  /* ---------------------------------------------------------------- */
  /* render                                                            */
  /* ---------------------------------------------------------------- */

  return (
    <div className="card flex flex-col" style={{ height: 640 }}>
      {/* Header */}
      <div className="flex items-center justify-between mb-3 flex-shrink-0">
        <h3 className="text-lg font-semibold text-white flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-dvmcp-purple" />
          AI Chat
        </h3>
        <div className="flex items-center gap-2">
          {usage.input_tokens > 0 && (
            <span className="text-xs text-gray-600">
              {(usage.input_tokens + usage.output_tokens).toLocaleString()} tokens
            </span>
          )}
          <button
            onClick={clearChat}
            className="text-gray-600 hover:text-gray-400 transition-colors p-1"
            title="Clear chat"
          >
            <Trash2 className="w-4 h-4" />
          </button>
          <button
            onClick={() => setShowSettings(!showSettings)}
            className={`p-1 rounded transition-colors ${
              showSettings ? 'text-dvmcp-purple' : 'text-gray-600 hover:text-gray-400'
            }`}
            title="Settings"
          >
            <Settings className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Settings panel */}
      {showSettings && (
        <div className="bg-dvmcp-bg rounded-lg p-3 mb-3 space-y-2 flex-shrink-0 border border-dvmcp-border">
          <div>
            <label className="text-xs text-gray-400 mb-1 block flex items-center gap-1">
              <Key className="w-3 h-3" /> Anthropic API Key
            </label>
            <input
              type="password"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              placeholder="sk-ant-api03-..."
              className="w-full bg-dvmcp-card border border-dvmcp-border rounded px-3 py-1.5 text-sm font-mono text-white placeholder-gray-600 focus:outline-none focus:border-dvmcp-purple"
            />
          </div>
          <div>
            <label className="text-xs text-gray-400 mb-1 block">Model</label>
            <select
              value={model}
              onChange={(e) => setModel(e.target.value)}
              className="w-full bg-dvmcp-card border border-dvmcp-border rounded px-3 py-1.5 text-sm text-white focus:outline-none focus:border-dvmcp-purple"
            >
              {MODELS.map((m) => (
                <option key={m.id} value={m.id}>
                  {m.label}
                </option>
              ))}
            </select>
          </div>
        </div>
      )}

      {/* Chat messages */}
      <div className="flex-1 overflow-y-auto space-y-3 mb-3 pr-1">
        {displayItems.length === 0 && !loading && (
          <div className="flex flex-col items-center justify-center h-full text-gray-600 select-none">
            <Bot className="w-10 h-10 mb-3 opacity-30" />
            <p className="text-sm">AI-Powered MCP Explorer</p>
            <p className="mt-1 text-xs text-gray-700 text-center max-w-sm">
              Chat with Claude to explore and exploit the challenge.
              Claude has direct access to this server's MCP tools and resources.
            </p>
            {!apiKey && (
              <p className="mt-3 text-xs text-dvmcp-yellow flex items-center gap-1">
                <Key className="w-3 h-3" /> Set your API key above to get started
              </p>
            )}
          </div>
        )}

        {displayItems.map((item) => {
          if (item.kind === 'user_text') {
            return (
              <div key={item.key} className="flex justify-end">
                <div className="flex items-start gap-2 max-w-[80%]">
                  <div className="bg-dvmcp-purple/20 border border-dvmcp-purple/30 rounded-xl rounded-tr-sm px-4 py-2.5">
                    <p className="text-sm text-gray-200 whitespace-pre-wrap">{item.text}</p>
                  </div>
                  <div className="w-7 h-7 rounded-full bg-dvmcp-purple/30 flex items-center justify-center flex-shrink-0 mt-0.5">
                    <User className="w-3.5 h-3.5 text-dvmcp-purple" />
                  </div>
                </div>
              </div>
            )
          }

          if (item.kind === 'assistant_text') {
            return (
              <div key={item.key} className="flex justify-start">
                <div className="flex items-start gap-2 max-w-[85%]">
                  <div className="w-7 h-7 rounded-full bg-dvmcp-blue/20 flex items-center justify-center flex-shrink-0 mt-0.5">
                    <Bot className="w-3.5 h-3.5 text-dvmcp-blue" />
                  </div>
                  <div className="bg-dvmcp-card border border-dvmcp-border rounded-xl rounded-tl-sm px-4 py-2.5">
                    <p className="text-sm text-gray-300 whitespace-pre-wrap">{item.text}</p>
                  </div>
                </div>
              </div>
            )
          }

          if (item.kind === 'tool_call') {
            const expanded = expandedTools[item.toolId || '']
            return (
              <div key={item.key} className="mx-9">
                <button
                  onClick={() => toggleToolExpand(item.toolId || '')}
                  className="w-full flex items-center gap-2 px-3 py-2 bg-dvmcp-bg border border-dvmcp-border rounded-lg text-left hover:border-dvmcp-yellow/40 transition-colors"
                >
                  <Wrench className="w-3.5 h-3.5 text-dvmcp-yellow flex-shrink-0" />
                  <span className="text-xs text-dvmcp-yellow font-semibold">Tool Call:</span>
                  <span className="text-xs text-dvmcp-green font-mono">{item.toolName}</span>
                  <span className="ml-auto">
                    {expanded ? (
                      <ChevronDown className="w-3.5 h-3.5 text-gray-600" />
                    ) : (
                      <ChevronRight className="w-3.5 h-3.5 text-gray-600" />
                    )}
                  </span>
                </button>
                {expanded && item.toolInput && (
                  <pre className="mt-1 bg-black/40 border border-dvmcp-border rounded-lg px-3 py-2 text-xs font-mono text-gray-400 overflow-x-auto">
                    {JSON.stringify(item.toolInput, null, 2)}
                  </pre>
                )}
              </div>
            )
          }

          if (item.kind === 'tool_result') {
            const expanded = expandedTools[item.toolId || '']
            return (
              <div key={item.key} className="mx-9">
                <button
                  onClick={() => toggleToolExpand('r_' + item.toolId)}
                  className={`w-full flex items-center gap-2 px-3 py-2 border rounded-lg text-left transition-colors ${
                    item.isError
                      ? 'bg-red-900/10 border-red-900/30 hover:border-red-700/40'
                      : 'bg-dvmcp-green/5 border-dvmcp-green/20 hover:border-dvmcp-green/40'
                  }`}
                >
                  <span
                    className={`w-1.5 h-1.5 rounded-full flex-shrink-0 ${
                      item.isError ? 'bg-red-500' : 'bg-dvmcp-green'
                    }`}
                  />
                  <span className={`text-xs font-semibold ${item.isError ? 'text-red-400' : 'text-dvmcp-green'}`}>
                    {item.isError ? 'Error' : 'Result'}
                  </span>
                  <span className="text-xs text-gray-500 truncate flex-1">
                    {(item.text || '').split('\n')[0].slice(0, 80)}
                  </span>
                  <span className="ml-auto flex-shrink-0">
                    {expandedTools['r_' + item.toolId] ? (
                      <ChevronDown className="w-3.5 h-3.5 text-gray-600" />
                    ) : (
                      <ChevronRight className="w-3.5 h-3.5 text-gray-600" />
                    )}
                  </span>
                </button>
                {expandedTools['r_' + item.toolId] && (
                  <pre
                    className={`mt-1 border rounded-lg px-3 py-2 text-xs font-mono overflow-x-auto max-h-60 overflow-y-auto ${
                      item.isError
                        ? 'bg-red-900/10 border-red-900/20 text-red-300'
                        : 'bg-black/40 border-dvmcp-border text-gray-300'
                    }`}
                  >
                    {item.text}
                  </pre>
                )}
              </div>
            )
          }

          return null
        })}

        {/* loading indicator */}
        {loading && (
          <div className="flex justify-start">
            <div className="flex items-start gap-2">
              <div className="w-7 h-7 rounded-full bg-dvmcp-blue/20 flex items-center justify-center flex-shrink-0">
                <Bot className="w-3.5 h-3.5 text-dvmcp-blue" />
              </div>
              <div className="bg-dvmcp-card border border-dvmcp-border rounded-xl rounded-tl-sm px-4 py-3">
                <div className="flex items-center gap-2 text-sm text-gray-400">
                  <Loader2 className="w-4 h-4 animate-spin text-dvmcp-blue" />
                  Thinking & executing tools...
                </div>
              </div>
            </div>
          </div>
        )}

        {/* error */}
        {error && (
          <div className="mx-2 flex items-start gap-2 bg-red-900/20 border border-red-900/30 rounded-lg px-3 py-2">
            <AlertCircle className="w-4 h-4 text-red-400 flex-shrink-0 mt-0.5" />
            <p className="text-xs text-red-300">{error}</p>
          </div>
        )}

        <div ref={chatEndRef} />
      </div>

      {/* Input */}
      <div className="flex gap-2 flex-shrink-0">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && send()}
          placeholder={
            !apiKey
              ? 'Set your API key first...'
              : 'Ask Claude to explore the challenge...'
          }
          disabled={!apiKey || loading}
          className="flex-1 bg-dvmcp-bg border border-dvmcp-border rounded-lg px-4 py-2.5 text-sm text-white placeholder-gray-600 focus:outline-none focus:border-dvmcp-purple disabled:opacity-50"
        />
        <button
          onClick={send}
          disabled={!apiKey || !input.trim() || loading}
          className="bg-dvmcp-purple hover:bg-purple-600 disabled:opacity-40 disabled:hover:bg-dvmcp-purple text-white font-semibold py-2.5 px-4 rounded-lg transition-colors flex items-center gap-2"
        >
          {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
        </button>
      </div>
    </div>
  )
}
