import { useEffect, useState } from 'react'
import { api } from '../utils/api'
import { CategoryBar, SkillRadar, DifficultyPie } from '../components/AnalyticsChart'
import { BarChart3, Users, Flag, Clock } from 'lucide-react'

export default function AnalyticsPage() {
  const [global, setGlobal] = useState<any>(null)
  const [personal, setPersonal] = useState<any>(null)

  useEffect(() => {
    api.getGlobalAnalytics().then(setGlobal).catch(() => {})
    api.getUserAnalytics().then(setPersonal).catch(() => {})
  }, [])

  const categoryData = [
    { name: 'Injection', solved: personal?.by_category?.Injection || 0, total: 3 },
    { name: 'Tool Manip.', solved: personal?.by_category?.['Tool Manipulation'] || 0, total: 4 },
    { name: 'Access Ctrl', solved: personal?.by_category?.['Access Control'] || 0, total: 3 },
    { name: 'Identity', solved: personal?.by_category?.Identity || 0, total: 3 },
    { name: 'Supply Chain', solved: personal?.by_category?.['Supply Chain'] || 0, total: 2 },
  ]

  const radarData = [
    { subject: 'Injection', score: (personal?.by_category?.Injection || 0) * 33, fullMark: 100 },
    { subject: 'Tools', score: (personal?.by_category?.['Tool Manipulation'] || 0) * 25, fullMark: 100 },
    { subject: 'Access', score: (personal?.by_category?.['Access Control'] || 0) * 33, fullMark: 100 },
    { subject: 'Identity', score: (personal?.by_category?.Identity || 0) * 33, fullMark: 100 },
    { subject: 'Supply Chain', score: (personal?.by_category?.['Supply Chain'] || 0) * 50, fullMark: 100 },
  ]

  const difficultyData = [
    { name: 'Easy', value: personal?.by_difficulty?.Easy || 0 },
    { name: 'Medium', value: personal?.by_difficulty?.Medium || 0 },
    { name: 'Hard', value: personal?.by_difficulty?.Hard || 0 },
  ]

  return (
    <div className="space-y-6">
      {global && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="card text-center">
            <Users className="w-6 h-6 text-dvmcp-blue mx-auto mb-2" />
            <div className="text-2xl font-bold text-white">{global.total_users}</div>
            <div className="text-xs text-gray-500">Total Users</div>
          </div>
          <div className="card text-center">
            <Flag className="w-6 h-6 text-dvmcp-green mx-auto mb-2" />
            <div className="text-2xl font-bold text-white">{global.total_correct_submissions}</div>
            <div className="text-xs text-gray-500">Flags Captured</div>
          </div>
          <div className="card text-center">
            <BarChart3 className="w-6 h-6 text-dvmcp-accent mx-auto mb-2" />
            <div className="text-2xl font-bold text-white">{global.total_submissions}</div>
            <div className="text-xs text-gray-500">Total Attempts</div>
          </div>
          <div className="card text-center">
            <Clock className="w-6 h-6 text-yellow-400 mx-auto mb-2" />
            <div className="text-2xl font-bold text-white">{global.most_solved_challenge || '-'}</div>
            <div className="text-xs text-gray-500">Most Solved</div>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h3 className="text-lg font-semibold text-white mb-4">Skill Radar</h3>
          <SkillRadar data={radarData} />
        </div>
        <div className="card">
          <h3 className="text-lg font-semibold text-white mb-4">Progress by Category</h3>
          <CategoryBar data={categoryData} />
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h3 className="text-lg font-semibold text-white mb-4">Completion by Difficulty</h3>
          <DifficultyPie data={difficultyData} />
        </div>
        {global?.challenge_stats && (
          <div className="card">
            <h3 className="text-lg font-semibold text-white mb-4">Challenge Solve Rates</h3>
            <div className="space-y-2 max-h-64 overflow-y-auto">
              {global.challenge_stats.map((cs: any) => (
                <div key={cs.id} className="flex items-center gap-3">
                  <span className="text-gray-500 text-xs w-8 text-right">#{cs.id}</span>
                  <div className="flex-1 bg-dvmcp-bg rounded-full h-2">
                    <div
                      className="bg-dvmcp-green h-2 rounded-full"
                      style={{ width: `${cs.solve_rate}%` }}
                    />
                  </div>
                  <span className="text-gray-400 text-xs w-12">{cs.solve_rate}%</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
