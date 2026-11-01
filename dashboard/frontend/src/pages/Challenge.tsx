import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { useStore } from '../stores/useStore'
import FlagSubmission from '../components/FlagSubmission'
import HintPanel from '../components/HintPanel'
import Playground from '../components/Playground'
import ChatPlayground from '../components/ChatPlayground'
import McpConfigSnippet from '../components/McpConfigSnippet'
import { ArrowLeft, Terminal, Shield, ExternalLink, BookOpen, Wrench, Sparkles, RotateCcw } from 'lucide-react'
import { api } from '../utils/api'

const ATTACK_INFO: Record<number, { vectors: string[]; objective: string; resources: string[] }> = {
  1: { vectors: ['Parameter injection in user_id', 'Prompt injection to access hidden resources'], objective: 'Access the hidden credentials resource via prompt injection', resources: ['OWASP Prompt Injection'] },
  2: { vectors: ['Hidden instructions in tool descriptions', '<IMPORTANT> tag injection'], objective: 'Discover and exploit hidden instructions in tool descriptions', resources: ['Tool Poisoning Attacks'] },
  3: { vectors: ['Path traversal', 'Unrestricted file access'], objective: 'Read files outside the intended directory scope', resources: ['OWASP Path Traversal'] },
  4: { vectors: ['Behavior mutation after trust established', 'Dynamic tool modification'], objective: 'Observe how tool behavior changes after repeated use', resources: ['Rug Pull Attacks'] },
  5: { vectors: ['Similar tool names', 'Hidden exfiltration in descriptions'], objective: 'Identify the malicious shadow tool and its hidden behavior', resources: ['Tool Shadowing'] },
  6: { vectors: ['Malicious content in documents', 'Instruction injection via data'], objective: 'Exploit injected instructions in document content', resources: ['Indirect Prompt Injection'] },
  7: { vectors: ['Token leakage in error messages', 'Debug info exposure'], objective: 'Extract leaked credentials from error responses and debug output', resources: ['OWASP Sensitive Data Exposure'] },
  8: { vectors: ['Arbitrary code execution', 'Weak input blocklist bypass'], objective: 'Execute arbitrary code through the code execution tools', resources: ['OWASP Code Injection'] },
  9: { vectors: ['Command injection in network tools', 'Shell metacharacter abuse'], objective: 'Inject OS commands through network diagnostic parameters', resources: ['OWASP Command Injection'] },
  10: { vectors: ['Chained: poisoning + file read + token theft + shadowing'], objective: 'Chain multiple vulnerabilities for full system compromise', resources: ['Multi-Vector Attacks'] },
  11: { vectors: ['Context injection via parameters', 'Identity claim manipulation'], objective: 'Inject false identity claims to gain admin access', resources: ['Identity Context Injection'] },
  12: { vectors: ['Undocumented internal parameter', 'Missing authorization on identity override'], objective: 'Discover a hidden tool parameter to read another employee\'s restricted HR record', resources: ['OWASP IDOR', 'Hidden API Surface'] },
  13: { vectors: ['Role confusion in shared state', 'Privilege escalation via context'], objective: 'Escalate from user to admin via role confusion', resources: ['Privilege Escalation'] },
  14: { vectors: ['Typosquatting in a shared plugin marketplace', 'Missing publisher/signature verification', 'Backdoored vendor release with hidden telemetry'], objective: 'Investigate a suspicious analytics plugin refresh, load the compromised plugin, and observe hidden prompt-injection plus data exfiltration behavior', resources: ['Supply Chain Attacks'] },
  15: { vectors: ['Public registry fallback with prefer-highest-version', 'Same package name in internal and public registries', 'Version confusion shadows trusted package'], objective: 'Act as a platform engineer investigating a suspicious post-release incident and discover that dependency confusion caused a malicious public package to replace a trusted internal one', resources: ['Dependency Confusion', 'Supply Chain Attacks'] },
}

export default function ChallengePage() {
  const { id } = useParams<{ id: string }>()
  const { challenges } = useStore()
  const [playgroundTab, setPlaygroundTab] = useState<'manual' | 'ai'>('ai')
  const [resetting, setResetting] = useState(false)
  const [resetMsg, setResetMsg] = useState<string | null>(null)
  const challengeId = parseInt(id || '0')
  const challenge = challenges.find((c) => c.id === challengeId)
  const info = ATTACK_INFO[challengeId]

  useEffect(() => {
    if (!challengeId) return
    api.recordEvent('challenge_view', challengeId).catch(() => {})
  }, [challengeId])

  if (!challenge) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">Challenge not found.</p>
        <Link to="/" className="text-dvmcp-accent hover:underline mt-2 inline-block">Back to challenges</Link>
      </div>
    )
  }

  return (
    <div className="space-y-6 max-w-6xl">
      <Link to="/" className="flex items-center gap-2 text-gray-400 hover:text-white text-sm">
        <ArrowLeft className="w-4 h-4" /> Back to Challenges
      </Link>

      <div className="card">
        <div className="flex items-start justify-between mb-4">
          <div>
            <div className="flex items-center gap-3 mb-1">
              <span className="text-gray-500 font-mono text-sm">Challenge {challenge.id}</span>
              <span className={
                challenge.difficulty === 'Easy' ? 'badge-easy' :
                challenge.difficulty === 'Medium' ? 'badge-medium' : 'badge-hard'
              }>{challenge.difficulty}</span>
              <span className="text-dvmcp-green font-bold text-sm">{challenge.points} pts</span>
            </div>
            <h1 className="text-2xl font-bold text-white">{challenge.name}</h1>
            <p className="text-gray-400 mt-2">{challenge.description}</p>
          </div>
          <Shield className="w-8 h-8 text-dvmcp-accent flex-shrink-0" />
        </div>

        <div className="bg-dvmcp-bg rounded-lg p-4 mt-4">
          <h3 className="text-sm font-semibold text-gray-300 mb-2 flex items-center gap-2">
            <Terminal className="w-4 h-4" /> Connection
          </h3>
          <code className="text-dvmcp-green text-sm">
            http://localhost:{challenge.port}/mcp
          </code>
          <p className="text-gray-500 text-xs mt-1">
            Streamable HTTP transport
          </p>
        </div>
      </div>

      <McpConfigSnippet challengeId={challengeId} port={challenge.port} />

      {info && (
        <div className="card">
          <h3 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
            <BookOpen className="w-5 h-5 text-dvmcp-blue" /> Attack Information
          </h3>
          <div className="space-y-3">
            <div>
              <span className="text-xs text-gray-500 uppercase tracking-wider">Objective</span>
              <p className="text-gray-300 text-sm mt-1">{info.objective}</p>
            </div>
            <div>
              <span className="text-xs text-gray-500 uppercase tracking-wider">Attack Vectors</span>
              <ul className="mt-1 space-y-1">
                {info.vectors.map((v, i) => (
                  <li key={i} className="text-gray-400 text-sm flex items-start gap-2">
                    <span className="text-dvmcp-accent">&#9656;</span> {v}
                  </li>
                ))}
              </ul>
            </div>
            <div>
              <span className="text-xs text-gray-500 uppercase tracking-wider">Resources</span>
              <div className="flex gap-2 mt-1 flex-wrap">
                {info.resources.map((r, i) => (
                  <span key={i} className="bg-dvmcp-bg text-gray-400 text-xs px-2 py-1 rounded flex items-center gap-1">
                    <ExternalLink className="w-3 h-3" /> {r}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Playground tabs */}
      <div>
        <div className="flex gap-1 mb-3 items-center">
          <button
            onClick={() => setPlaygroundTab('ai')}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              playgroundTab === 'ai'
                ? 'bg-dvmcp-purple/20 text-dvmcp-purple border border-dvmcp-purple/30'
                : 'text-gray-400 hover:text-white hover:bg-dvmcp-border/50 border border-transparent'
            }`}
          >
            <Sparkles className="w-4 h-4" /> AI Chat
          </button>
          <button
            onClick={() => setPlaygroundTab('manual')}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              playgroundTab === 'manual'
                ? 'bg-dvmcp-yellow/20 text-dvmcp-yellow border border-dvmcp-yellow/30'
                : 'text-gray-400 hover:text-white hover:bg-dvmcp-border/50 border border-transparent'
            }`}
          >
            <Wrench className="w-4 h-4" /> Manual Explorer
          </button>
          {[12, 13, 14, 15].includes(challengeId) && (
            <>
              <button
                onClick={async () => {
                  setResetting(true)
                  setResetMsg(null)
                  try {
                    const res = await api.playgroundReset(challengeId)
                    setResetMsg(res.status === 'ok' ? 'Challenge state reset!' : res.message)
                  } catch (e: any) {
                    setResetMsg(e.message || 'Reset failed')
                  } finally {
                    setResetting(false)
                    setTimeout(() => setResetMsg(null), 3000)
                  }
                }}
                disabled={resetting}
                className="ml-auto flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors text-dvmcp-red hover:bg-dvmcp-red/10 border border-dvmcp-red/30 disabled:opacity-50"
              >
                <RotateCcw className={`w-4 h-4 ${resetting ? 'animate-spin' : ''}`} /> {resetting ? 'Resetting…' : 'Reset State'}
              </button>
              {resetMsg && (
                <span className="text-xs text-dvmcp-green ml-2">{resetMsg}</span>
              )}
            </>
          )}
        </div>
        <div style={{ display: playgroundTab === 'ai' ? 'block' : 'none' }}>
          <ChatPlayground challengeId={challengeId} />
        </div>
        <div style={{ display: playgroundTab === 'manual' ? 'block' : 'none' }}>
          <Playground challengeId={challengeId} />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <FlagSubmission challengeId={challengeId} />
        <HintPanel challengeId={challengeId} hints={challenge.hints || []} />
      </div>
    </div>
  )
}
