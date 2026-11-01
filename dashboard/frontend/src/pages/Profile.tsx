import { useEffect, useState } from 'react'
import { useStore } from '../stores/useStore'
import { api } from '../utils/api'
import { User, Award, Clock, Target } from 'lucide-react'

export default function ProfilePage() {
  const { user } = useStore()
  const [progress, setProgress] = useState<any[]>([])

  useEffect(() => {
    api.getProgress().then(setProgress).catch(() => {})
  }, [])

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div className="card">
        <div className="flex items-center gap-4">
          <div className="w-16 h-16 bg-dvmcp-accent/20 rounded-full flex items-center justify-center">
            <User className="w-8 h-8 text-dvmcp-accent" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-white">{user?.username || 'Player'}</h1>
            <p className="text-gray-500">DVMCP Hacker</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-4">
        <div className="card text-center">
          <Award className="w-6 h-6 text-dvmcp-green mx-auto mb-2" />
          <div className="text-2xl font-bold text-white">{user?.total_points || 0}</div>
          <div className="text-xs text-gray-500">Total Points</div>
        </div>
        <div className="card text-center">
          <Target className="w-6 h-6 text-dvmcp-accent mx-auto mb-2" />
          <div className="text-2xl font-bold text-white">{user?.challenges_completed || 0}</div>
          <div className="text-xs text-gray-500">Completed</div>
        </div>
        <div className="card text-center">
          <Clock className="w-6 h-6 text-dvmcp-blue mx-auto mb-2" />
          <div className="text-2xl font-bold text-white">15</div>
          <div className="text-xs text-gray-500">Total Challenges</div>
        </div>
      </div>

      <div className="card">
        <h3 className="text-lg font-semibold text-white mb-4">Submission History</h3>
        <div className="space-y-2">
          {progress.length === 0 && (
            <p className="text-gray-500 text-sm">No submissions yet. Start hacking!</p>
          )}
          {progress.map((p: any, i: number) => (
            <div key={i} className="flex items-center justify-between bg-dvmcp-bg rounded-lg px-4 py-3">
              <div>
                <span className="text-white font-medium">Challenge {p.challenge_id}</span>
                <span className={`ml-3 text-xs ${p.status === 'completed' ? 'text-green-400' : 'text-yellow-400'}`}>
                  {p.status}
                </span>
              </div>
              {p.completed_at && (
                <span className="text-gray-500 text-xs">{new Date(p.completed_at).toLocaleDateString()}</span>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
