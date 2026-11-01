import { useStore } from '../stores/useStore'
import { Trophy, Medal } from 'lucide-react'

const rankColors = ['text-yellow-400', 'text-gray-300', 'text-orange-400']

export default function Leaderboard({ compact = false }: { compact?: boolean }) {
  const { leaderboard } = useStore()
  const entries = compact ? (leaderboard || []).slice(0, 10) : (leaderboard || [])

  return (
    <div className="card">
      <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
        <Trophy className="w-5 h-5 text-yellow-400" />
        {compact ? 'Top 10' : 'Leaderboard'}
      </h3>
      <div className="space-y-2">
        <div className="grid grid-cols-12 text-xs text-gray-500 px-3 pb-2 border-b border-dvmcp-border">
          <span className="col-span-1">#</span>
          <span className="col-span-5">Player</span>
          <span className="col-span-3 text-right">Score</span>
          <span className="col-span-3 text-right">Solved</span>
        </div>
        {entries.map((entry) => (
          <div
            key={entry.rank}
            className="grid grid-cols-12 items-center px-3 py-2 rounded-lg hover:bg-dvmcp-border/30 text-sm"
          >
            <span className={`col-span-1 font-bold ${rankColors[entry.rank - 1] || 'text-gray-400'}`}>
              {entry.rank <= 3 ? <Medal className="w-4 h-4 inline" /> : entry.rank}
            </span>
            <span className="col-span-5 text-white font-medium truncate">{entry.username}</span>
            <span className="col-span-3 text-right text-dvmcp-green font-bold">{entry.total_points}</span>
            <span className="col-span-3 text-right text-gray-400">{entry.challenges_completed}/15</span>
          </div>
        ))}
        {entries.length === 0 && (
          <p className="text-gray-500 text-sm text-center py-4">No submissions yet.</p>
        )}
      </div>
    </div>
  )
}
