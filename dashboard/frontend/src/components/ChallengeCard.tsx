import { Link } from 'react-router-dom'
import { Lock, CheckCircle2, Play, Terminal } from 'lucide-react'
import type { Challenge } from '../stores/useStore'

const difficultyBadge: Record<string, string> = {
  Easy: 'badge-easy',
  Medium: 'badge-medium',
  Hard: 'badge-hard',
}

const categoryColors: Record<string, string> = {
  Injection: 'text-blue-400',
  'Tool Manipulation': 'text-purple-400',
  'Access Control': 'text-yellow-400',
  'Identity': 'text-cyan-400',
  'Supply Chain': 'text-orange-400',
}

const statusIcon = {
  not_started: <Lock className="w-5 h-5 text-gray-600" />,
  in_progress: <Play className="w-5 h-5 text-yellow-400" />,
  completed: <CheckCircle2 className="w-5 h-5 text-green-400" />,
}

export default function ChallengeCard({ challenge }: { challenge: Challenge }) {
  return (
    <Link
      to={`/challenge/${challenge.id}`}
      className="card hover:border-dvmcp-accent/50 transition-all hover:shadow-lg hover:shadow-dvmcp-accent/5 group"
    >
      <div className="flex justify-between items-start mb-3">
        <span className={difficultyBadge[challenge.difficulty]}>
          {challenge.difficulty}
        </span>
        {statusIcon[challenge.status]}
      </div>
      <div className="mb-2">
        <span className="text-gray-500 text-xs font-mono">Challenge {challenge.id}</span>
        <h3 className="text-white font-semibold group-hover:text-dvmcp-accent transition-colors">
          {challenge.name}
        </h3>
      </div>
      <p className="text-gray-400 text-sm mb-3 line-clamp-2">{challenge.description}</p>
      <div className="flex justify-between items-center text-xs">
        <span className={categoryColors[challenge.category] || 'text-gray-400'}>
          {challenge.category}
        </span>
        <span className="text-dvmcp-green font-bold">{challenge.points} pts</span>
      </div>
      <div className="mt-3 pt-3 border-t border-dvmcp-border flex items-center gap-2 text-xs text-gray-500">
        <Terminal className="w-3 h-3" />
        <code>localhost:{challenge.port}</code>
      </div>
    </Link>
  )
}
