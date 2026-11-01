import { useState, useRef, useEffect } from 'react'
import { api } from '../utils/api'
import {
  Terminal, Play, Plug, Wrench, Database, Trash2,
  Loader2, ChevronRight, ChevronDown, Copy, Check,
  Zap, Eye, AlertTriangle,
} from 'lucide-react'

/* ------------------------------------------------------------------ */
/* Types                                                               */
/* ------------------------------------------------------------------ */

interface Tool {
  name: string
  description: string
  inputSchema: {
    type?: string
    properties?: Record<string, { type?: string; title?: string; description?: string }>
    required?: string[]
  }
}

interface Resource {
  uri: string
  name: string
  description: string
}

interface LogEntry {
  id: number
  type: 'command' | 'result' | 'error' | 'info' | 'system'
  timestamp: string
  content: string
}

let _logId = 0

/* ------------------------------------------------------------------ */
/* Component                                                           */
/* ------------------------------------------------------------------ */

export default function Playground({ challengeId }: { challengeId: number }) {
  const [status, setStatus] = useState<'disconnected' | 'connecting' | 'connected' | 'error'>('disconnected')
  const [tools, setTools] = useState<Tool[]>([])
  const [resources, setResources] = useState<Resource[]>([])
  const [expandedTool, setExpandedTool] = useState<string | null>(null)
  const [toolArgs, setToolArgs] = useState<Record<string, string>>({})
  const [executing, setExecuting] = useState(false)
  const [log, setLog] = useState<LogEntry[]>([])
  const [copied, setCopied] = useState<number | null>(null)
  const [resourceUri, setResourceUri] = useState('')
  const outputRef = useRef<HTMLDivElement>(null)

  /* helpers --------------------------------------------------------- */

  const addLog = (type: LogEntry['type'], content: string) => {
    const entry: LogEntry = {
      id: ++_logId,
      type,
      timestamp: new Date().toLocaleTimeString('en-US', { hour12: false }),
      content,
    }
    setLog((prev) => [...prev, entry])
  }

  // auto-scroll terminal on new entries
  useEffect(() => {
    if (outputRef.current) {
      outputRef.current.scrollTop = outputRef.current.scrollHeight
    }
  }, [log])

  /* actions --------------------------------------------------------- */

  const connect = async () => {
    setStatus('connecting')
    addLog('system', `Connecting to Challenge ${challengeId} (port ${9000 + challengeId})...`)
    try {
      const info = await api.playgroundInfo(challengeId)
      setTools(info.tools)
      setResources(info.resources)
      setStatus('connected')
      addLog('info', `Connected. ${info.tools.length} tool(s), ${info.resources.length} resource(s) available.`)
      info.tools.forEach((t: Tool) => addLog('info', `  tool  ${t.name}`))
      info.resources.forEach((r: Resource) => addLog('info', `  res   ${r.uri}`))
    } catch (e: any) {
      setStatus('error')
      addLog('error', `Connection failed: ${e.message}`)
    }
  }

  const callTool = async (toolName: string) => {
    const tool = tools.find((t) => t.name === toolName)
    if (!tool) return

    const args: Record<string, any> = {}
    const props = tool.inputSchema?.properties || {}
    for (const [key, schema] of Object.entries(props)) {
      const raw = toolArgs[`${toolName}.${key}`]
      if (raw !== undefined && raw !== '') {
        switch (schema.type) {
          case 'integer':
            args[key] = parseInt(raw, 10); break
          case 'number':
            args[key] = parseFloat(raw); break
          case 'boolean':
            args[key] = raw.toLowerCase() === 'true'; break
          case 'object':
          case 'array':
            try { args[key] = JSON.parse(raw) } catch { args[key] = raw }
            break
          default:
            args[key] = raw
        }
      }
    }

    const argsStr = Object.keys(args).length > 0 ? ' ' + JSON.stringify(args) : ''
    addLog('command', `> call_tool ${toolName}${argsStr}`)
    setExecuting(true)

    try {
      const result = await api.playgroundCallTool(challengeId, toolName, args)
      const text = result.content.map((c: any) => c.text || c.data || '').join('\n')
      addLog(result.isError ? 'error' : 'result', text)
    } catch (e: any) {
      addLog('error', `Error: ${e.message}`)
    } finally {
      setExecuting(false)
    }
  }

  const readResource = async (uri: string) => {
    addLog('command', `> read_resource ${uri}`)
    setExecuting(true)
    try {
      const result = await api.playgroundReadResource(challengeId, uri)
      const text = result.contents.map((c: any) => c.text || c.data || '').join('\n')
      addLog('result', text)
    } catch (e: any) {
      addLog('error', `Error: ${e.message}`)
    } finally {
      setExecuting(false)
    }
  }

  const copyText = (text: string, id: number) => {
    navigator.clipboard.writeText(text)
    setCopied(id)
    setTimeout(() => setCopied(null), 2000)
  }

  /* ---------------------------------------------------------------- */
  /* render                                                            */
  /* ---------------------------------------------------------------- */

  return (
    <div className="card">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-white flex items-center gap-2">
          <Zap className="w-5 h-5 text-dvmcp-yellow" />
          MCP Playground
        </h3>
        <div className="flex items-center gap-3">
          {/* status pill */}
          <span
            className={`flex items-center gap-1.5 text-xs ${
              status === 'connected'
                ? 'text-dvmcp-green'
                : status === 'connecting'
                ? 'text-dvmcp-yellow'
                : status === 'error'
                ? 'text-red-400'
                : 'text-gray-500'
            }`}
          >
            <span
              className={`w-2 h-2 rounded-full ${
                status === 'connected'
                  ? 'bg-dvmcp-green'
                  : status === 'connecting'
                  ? 'bg-dvmcp-yellow animate-pulse'
                  : status === 'error'
                  ? 'bg-red-400'
                  : 'bg-gray-600'
              }`}
            />
            {status === 'connected'
              ? 'Connected'
              : status === 'connecting'
              ? 'Connecting...'
              : status === 'error'
              ? 'Error'
              : 'Disconnected'}
          </span>
          <button
            onClick={connect}
            disabled={status === 'connecting'}
            className="btn-primary text-sm flex items-center gap-1.5 py-1.5 px-3"
          >
            {status === 'connecting' ? (
              <Loader2 className="w-3.5 h-3.5 animate-spin" />
            ) : (
              <Plug className="w-3.5 h-3.5" />
            )}
            {status === 'connected' ? 'Reconnect' : 'Connect'}
          </button>
        </div>
      </div>

      {/* Main layout */}
      <div className="grid grid-cols-1 lg:grid-cols-5 gap-4">
        {/* ---- Left panel: controls ---- */}
        <div className="lg:col-span-2 space-y-3">
          {/* Tools */}
          <div className="bg-dvmcp-bg rounded-lg p-3">
            <h4 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2 flex items-center gap-1.5">
              <Wrench className="w-3.5 h-3.5" /> Tools ({tools.length})
            </h4>

            {tools.length === 0 ? (
              <p className="text-gray-600 text-xs italic">Connect to discover tools</p>
            ) : (
              <div className="space-y-1.5">
                {tools.map((tool) => (
                  <div
                    key={tool.name}
                    className="border border-dvmcp-border rounded-lg overflow-hidden"
                  >
                    {/* tool header */}
                    <button
                      onClick={() =>
                        setExpandedTool(expandedTool === tool.name ? null : tool.name)
                      }
                      className="w-full flex items-center gap-2 px-3 py-2 text-left hover:bg-dvmcp-card/60 transition-colors"
                    >
                      {expandedTool === tool.name ? (
                        <ChevronDown className="w-3.5 h-3.5 text-dvmcp-accent flex-shrink-0" />
                      ) : (
                        <ChevronRight className="w-3.5 h-3.5 text-gray-500 flex-shrink-0" />
                      )}
                      <span className="text-dvmcp-green font-mono text-sm truncate">
                        {tool.name}
                      </span>
                    </button>

                    {/* expanded: description + args + execute */}
                    {expandedTool === tool.name && (
                      <div className="px-3 pb-3 space-y-2 border-t border-dvmcp-border">
                        {tool.description && (
                          <details className="mt-2">
                            <summary className="text-xs text-gray-500 cursor-pointer hover:text-gray-400 select-none">
                              Description
                            </summary>
                            <pre className="text-gray-500 text-xs mt-1 whitespace-pre-wrap bg-black/30 rounded p-2 max-h-40 overflow-y-auto">
                              {tool.description}
                            </pre>
                          </details>
                        )}

                        {tool.inputSchema?.properties &&
                          Object.entries(tool.inputSchema.properties).map(
                            ([key, schema]) => (
                              <div key={key}>
                                <label className="text-xs text-gray-400 flex items-center gap-1 mb-1">
                                  {key}
                                  {tool.inputSchema.required?.includes(key) && (
                                    <span className="text-dvmcp-accent">*</span>
                                  )}
                                  <span className="text-gray-600">
                                    ({schema.type || 'string'})
                                  </span>
                                </label>
                                <input
                                  type="text"
                                  value={toolArgs[`${tool.name}.${key}`] || ''}
                                  onChange={(e) =>
                                    setToolArgs((prev) => ({
                                      ...prev,
                                      [`${tool.name}.${key}`]: e.target.value,
                                    }))
                                  }
                                  placeholder={schema.description || key}
                                  className="w-full bg-dvmcp-card border border-dvmcp-border rounded px-2 py-1.5 text-xs font-mono text-white placeholder-gray-600 focus:outline-none focus:border-dvmcp-accent"
                                />
                              </div>
                            ),
                          )}

                        <button
                          onClick={() => callTool(tool.name)}
                          disabled={executing}
                          className="w-full btn-primary text-xs py-1.5 flex items-center justify-center gap-1.5 mt-1"
                        >
                          {executing ? (
                            <Loader2 className="w-3 h-3 animate-spin" />
                          ) : (
                            <Play className="w-3 h-3" />
                          )}
                          Execute
                        </button>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Resources */}
          <div className="bg-dvmcp-bg rounded-lg p-3">
            <h4 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2 flex items-center gap-1.5">
              <Database className="w-3.5 h-3.5" /> Resources ({resources.length})
            </h4>

            {resources.length === 0 ? (
              <p className="text-gray-600 text-xs italic">Connect to discover resources</p>
            ) : (
              <div className="space-y-1.5">
                {resources.map((res) => (
                  <button
                    key={res.uri}
                    onClick={() => readResource(res.uri)}
                    disabled={executing}
                    className="w-full flex items-center gap-2 px-3 py-2 bg-dvmcp-card border border-dvmcp-border rounded-lg text-left hover:border-dvmcp-blue/50 transition-colors group"
                  >
                    <Eye className="w-3.5 h-3.5 text-gray-500 group-hover:text-dvmcp-blue flex-shrink-0" />
                    <div className="min-w-0 flex-1">
                      <span className="text-dvmcp-blue font-mono text-xs block truncate">
                        {res.uri}
                      </span>
                      {res.description && (
                        <span className="text-gray-600 text-xs block truncate">
                          {res.description}
                        </span>
                      )}
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>

          <form
            className="flex gap-2"
            onSubmit={(e) => {
              e.preventDefault()
              const uri = resourceUri.trim()
              if (!uri || executing) return
              readResource(uri)
            }}
          >
            <input
              type="text"
              value={resourceUri}
              onChange={(e) => setResourceUri(e.target.value)}
              placeholder="Read a resource URI you discovered"
              className="flex-1 bg-dvmcp-card border border-dvmcp-border rounded px-2 py-1.5 text-xs font-mono text-white placeholder-gray-600 focus:outline-none focus:border-dvmcp-accent"
            />
            <button
              type="submit"
              disabled={executing || !resourceUri.trim()}
              className="btn-primary text-xs py-1.5 px-3"
            >
              Read
            </button>
          </form>

          {/* Warning */}
          <div className="flex items-start gap-2 text-xs text-gray-600 px-1">
            <AlertTriangle className="w-3.5 h-3.5 flex-shrink-0 mt-0.5 text-dvmcp-yellow/60" />
            <span>
              This playground connects directly to the vulnerable MCP servers.
              Explore tools and resources to discover flags.
            </span>
          </div>
        </div>

        {/* ---- Right panel: terminal output ---- */}
        <div className="lg:col-span-3">
          <div className="bg-black rounded-lg border border-dvmcp-border overflow-hidden flex flex-col" style={{ height: 520 }}>
            {/* terminal chrome */}
            <div className="flex items-center justify-between px-3 py-2 bg-dvmcp-bg/80 border-b border-dvmcp-border">
              <div className="flex items-center gap-2">
                <div className="flex gap-1.5">
                  <span className="w-2.5 h-2.5 rounded-full bg-red-500/80" />
                  <span className="w-2.5 h-2.5 rounded-full bg-yellow-500/80" />
                  <span className="w-2.5 h-2.5 rounded-full bg-green-500/80" />
                </div>
                <span className="text-xs text-gray-500 font-mono ml-2">
                  mcp-playground ~ challenge-{challengeId}
                </span>
              </div>
              <button
                onClick={() => setLog([])}
                className="text-gray-600 hover:text-gray-400 transition-colors"
                title="Clear output"
              >
                <Trash2 className="w-3.5 h-3.5" />
              </button>
            </div>

            {/* terminal body */}
            <div
              ref={outputRef}
              className="flex-1 overflow-y-auto p-3 font-mono text-xs leading-relaxed space-y-0.5"
            >
              {log.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-full text-gray-600 select-none">
                  <Terminal className="w-10 h-10 mb-3 opacity-30" />
                  <p className="text-sm">MCP Playground</p>
                  <p className="mt-1 text-gray-700 text-xs">
                    Click <strong className="text-gray-500">Connect</strong> to start
                    exploring the challenge server
                  </p>
                  <div className="mt-4 text-gray-700 text-left space-y-1">
                    <p>1. Connect to the MCP server</p>
                    <p>2. Browse available tools and resources</p>
                    <p>3. Call tools with custom arguments</p>
                    <p>4. Read resources to find hidden data</p>
                    <p>5. Discover the flag!</p>
                  </div>
                </div>
              ) : (
                log.map((entry) => (
                  <div key={entry.id} className="group flex items-start gap-2">
                    <span className="text-gray-700 flex-shrink-0 select-none">
                      [{entry.timestamp}]
                    </span>
                    <pre
                      className={`whitespace-pre-wrap break-all flex-1 ${
                        entry.type === 'command'
                          ? 'text-dvmcp-green font-semibold'
                          : entry.type === 'result'
                          ? 'text-gray-300'
                          : entry.type === 'error'
                          ? 'text-red-400'
                          : entry.type === 'system'
                          ? 'text-dvmcp-yellow'
                          : 'text-dvmcp-blue'
                      }`}
                    >
                      {entry.content}
                    </pre>
                    {(entry.type === 'result' || entry.type === 'error') && (
                      <button
                        onClick={() => copyText(entry.content, entry.id)}
                        className="opacity-0 group-hover:opacity-100 text-gray-600 hover:text-gray-400 transition-all flex-shrink-0 mt-0.5"
                        title="Copy to clipboard"
                      >
                        {copied === entry.id ? (
                          <Check className="w-3 h-3 text-dvmcp-green" />
                        ) : (
                          <Copy className="w-3 h-3" />
                        )}
                      </button>
                    )}
                  </div>
                ))
              )}
              {executing && (
                <div className="flex items-center gap-2 text-dvmcp-yellow">
                  <Loader2 className="w-3 h-3 animate-spin" />
                  <span>Executing...</span>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
