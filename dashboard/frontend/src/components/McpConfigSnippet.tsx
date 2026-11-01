import { useState } from 'react'
import { Copy, Check, Plug } from 'lucide-react'

interface Props {
  challengeId: number
  port: number
}

type ClientKey = 'claude-code' | 'cursor' | 'vscode' | 'windsurf' | 'cli'

const CLIENTS: { key: ClientKey; label: string; hint: string }[] = [
  { key: 'claude-code', label: 'Claude Code', hint: 'Save as .mcp.json at project root (or ~/.claude.json for global)' },
  { key: 'cursor', label: 'Cursor', hint: 'Save as .cursor/mcp.json in project, or ~/.cursor/mcp.json globally' },
  { key: 'vscode', label: 'VS Code', hint: 'Save as .vscode/mcp.json (uses "servers" key, not "mcpServers")' },
  { key: 'windsurf', label: 'Windsurf', hint: 'Save as ~/.codeium/windsurf/mcp_config.json' },
  { key: 'cli', label: 'Claude CLI', hint: 'Run this in your terminal to register the server globally' },
]

function buildSnippet(client: ClientKey, challengeId: number, port: number): string {
  const name = `dvmcp-challenge${challengeId}`
  const url = `http://localhost:${port}/mcp`

  if (client === 'cli') {
    return `claude mcp add --transport http ${name} ${url}`
  }

  if (client === 'vscode') {
    return JSON.stringify(
      {
        servers: {
          [name]: {
            type: 'http',
            url,
          },
        },
      },
      null,
      2,
    )
  }

  // Claude Code, Cursor, Windsurf all use the same shape
  return JSON.stringify(
    {
      mcpServers: {
        [name]: {
          type: 'http',
          url,
        },
      },
    },
    null,
    2,
  )
}

export default function McpConfigSnippet({ challengeId, port }: Props) {
  const [active, setActive] = useState<ClientKey>('claude-code')
  const [copied, setCopied] = useState(false)

  const snippet = buildSnippet(active, challengeId, port)
  const activeMeta = CLIENTS.find((c) => c.key === active)!

  const copy = () => {
    navigator.clipboard.writeText(snippet)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className="card">
      <h3 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
        <Plug className="w-5 h-5 text-dvmcp-accent" /> Add to your MCP client
      </h3>

      <div className="flex gap-1 mb-3 flex-wrap">
        {CLIENTS.map((c) => (
          <button
            key={c.key}
            onClick={() => setActive(c.key)}
            className={`px-3 py-1.5 rounded-md text-xs font-medium transition-colors ${
              active === c.key
                ? 'bg-dvmcp-accent/20 text-dvmcp-accent border border-dvmcp-accent/30'
                : 'text-gray-400 hover:text-white hover:bg-dvmcp-border/50 border border-transparent'
            }`}
          >
            {c.label}
          </button>
        ))}
      </div>

      <p className="text-xs text-gray-500 mb-2">{activeMeta.hint}</p>

      <div className="relative">
        <pre className="bg-dvmcp-bg rounded-lg p-4 text-xs text-dvmcp-green overflow-x-auto font-mono border border-dvmcp-border">
{snippet}
        </pre>
        <button
          onClick={copy}
          className="absolute top-2 right-2 flex items-center gap-1 px-2 py-1 rounded bg-dvmcp-border/70 hover:bg-dvmcp-border text-gray-300 text-xs"
          title="Copy to clipboard"
        >
          {copied ? (
            <>
              <Check className="w-3 h-3 text-dvmcp-green" /> Copied
            </>
          ) : (
            <>
              <Copy className="w-3 h-3" /> Copy
            </>
          )}
        </button>
      </div>
    </div>
  )
}
