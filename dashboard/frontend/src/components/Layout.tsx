import { Outlet, Link, useNavigate, useLocation } from 'react-router-dom'
import { useStore } from '../stores/useStore'
import { useEffect } from 'react'
import { api } from '../utils/api'
import { Shield, Trophy, BarChart3, User, LogOut, Skull } from 'lucide-react'

function loadChallenges(setChallenges: (c: any[]) => void) {
  Promise.all([api.getChallenges(), api.getProgress().catch(() => [])])
    .then(([challenges, progress]) => {
      const statusByChallenge: Record<number, string> = {}
      for (const p of progress as any[]) statusByChallenge[p.challenge_id] = p.status
      setChallenges(
        (challenges as any[]).map((c) => ({
          ...c,
          status: statusByChallenge[c.id] || 'not_started',
        })),
      )
    })
    .catch(() => {})
}

export default function Layout() {
  const { user, token, setUser, logout, connectWs, setChallenges, setLeaderboard } = useStore()
  const navigate = useNavigate()
  const location = useLocation()

  useEffect(() => {
    if (!token) { navigate('/login'); return }
    api.getProfile().then(setUser).catch(() => { logout(); navigate('/login') })
    loadChallenges(setChallenges)
    api.getLeaderboard().then(setLeaderboard).catch(() => {})
    connectWs()
  }, [token])

  useEffect(() => {
    if (token && location.pathname === '/') {
      loadChallenges(setChallenges)
    }
  }, [location.pathname])

  const nav = [
    { to: '/', icon: Shield, label: 'Challenges' },
    { to: '/leaderboard', icon: Trophy, label: 'Leaderboard' },
    { to: '/analytics', icon: BarChart3, label: 'Analytics' },
    { to: '/profile', icon: User, label: 'Profile' },
  ]

  return (
    <div className="min-h-screen flex flex-col">
      <header className="bg-dvmcp-card border-b border-dvmcp-border px-6 py-3 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-3">
          <Skull className="w-8 h-8 text-dvmcp-accent" />
          <div>
            <h1 className="text-xl font-bold text-white">DVMCP <span className="text-dvmcp-accent">v2.0</span></h1>
            <p className="text-xs text-gray-500">Damn Vulnerable MCP Server</p>
          </div>
        </Link>
        <nav className="flex items-center gap-1">
          {nav.map(({ to, icon: Icon, label }) => (
            <Link
              key={to}
              to={to}
              className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm transition-colors ${
                location.pathname === to
                  ? 'bg-dvmcp-accent/20 text-dvmcp-accent'
                  : 'text-gray-400 hover:text-white hover:bg-dvmcp-border/50'
              }`}
            >
              <Icon className="w-4 h-4" />
              {label}
            </Link>
          ))}
        </nav>
        <div className="flex items-center gap-4">
          {user && (
            <div className="text-sm">
              <span className="text-gray-400">Score:</span>{' '}
              <span className="text-dvmcp-green font-bold">{user.total_points}</span>
            </div>
          )}
          <button onClick={() => { logout(); navigate('/login') }} className="text-gray-500 hover:text-white">
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </header>
      <main className="flex-1 p-6 max-w-7xl mx-auto w-full">
        <Outlet />
      </main>
    </div>
  )
}
