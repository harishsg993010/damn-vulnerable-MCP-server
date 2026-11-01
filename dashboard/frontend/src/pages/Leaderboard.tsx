import { useEffect } from 'react'
import { useStore } from '../stores/useStore'
import { api } from '../utils/api'
import LeaderboardComponent from '../components/Leaderboard'

export default function LeaderboardPage() {
  const { setLeaderboard } = useStore()

  useEffect(() => {
    api.getLeaderboard().then(setLeaderboard).catch(() => {})
  }, [])

  return (
    <div className="max-w-3xl mx-auto">
      <LeaderboardComponent />
    </div>
  )
}
