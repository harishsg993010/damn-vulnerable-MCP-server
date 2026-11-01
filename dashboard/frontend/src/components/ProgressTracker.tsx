import { useStore } from '../stores/useStore'
import { Target, Zap } from 'lucide-react'

export default function ProgressTracker() {
  const { challenges, user } = useStore()
  const completed = challenges.filter((c) => c.status === 'completed').length
  const total = challenges.length || 15
  const pct = Math.round((completed / total) * 100)

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-white flex items-center gap-2">
          <Target className="w-5 h-5 text-dvmcp-accent" />
          Your Progress
        </h3>
        <span className="text-2xl font-bold text-dvmcp-green">{pct}%</span>
      </div>
      <div className="w-full bg-dvmcp-bg rounded-full h-3 mb-4">
        <div
          className="bg-gradient-to-r from-dvmcp-accent to-dvmcp-green h-3 rounded-full transition-all duration-500"
          style={{ width: `${pct}%` }}
        />
      </div>
      <div className="grid grid-cols-3 gap-4 text-center">
        <div>
          <div className="text-2xl font-bold text-white">{completed}</div>
          <div className="text-xs text-gray-500">Completed</div>
        </div>
        <div>
          <div className="text-2xl font-bold text-white">{total - completed}</div>
          <div className="text-xs text-gray-500">Remaining</div>
        </div>
        <div>
          <div className="text-2xl font-bold text-dvmcp-green flex items-center justify-center gap-1">
            <Zap className="w-4 h-4" />
            {user?.total_points || 0}
          </div>
          <div className="text-xs text-gray-500">Points</div>
        </div>
      </div>
    </div>
  )
}
