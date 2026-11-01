import { useStore } from '../stores/useStore'
import ChallengeGrid from '../components/ChallengeGrid'
import ProgressTracker from '../components/ProgressTracker'
import Leaderboard from '../components/Leaderboard'
import { Filter } from 'lucide-react'

const FILTERS = ['All', 'Easy', 'Medium', 'Hard']
const CATEGORIES = ['Injection', 'Tool Manipulation', 'Access Control', 'Identity', 'Supply Chain']

export default function Dashboard() {
  const { filter, setFilter } = useStore()

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <ProgressTracker />
        </div>
        <Leaderboard compact />
      </div>

      <div className="flex items-center gap-3 flex-wrap">
        <Filter className="w-4 h-4 text-gray-500" />
        {FILTERS.map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`px-3 py-1.5 rounded-lg text-sm transition-colors ${
              filter === f
                ? 'bg-dvmcp-accent text-white'
                : 'bg-dvmcp-card text-gray-400 hover:text-white border border-dvmcp-border'
            }`}
          >
            {f}
          </button>
        ))}
        <span className="text-gray-600 mx-2">|</span>
        {CATEGORIES.map((c) => (
          <button
            key={c}
            onClick={() => setFilter(c)}
            className={`px-3 py-1.5 rounded-lg text-sm transition-colors ${
              filter === c
                ? 'bg-dvmcp-purple text-white'
                : 'bg-dvmcp-card text-gray-400 hover:text-white border border-dvmcp-border'
            }`}
          >
            {c}
          </button>
        ))}
      </div>

      <ChallengeGrid />
    </div>
  )
}
