import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useStore } from '../stores/useStore'
import { api } from '../utils/api'
import { Skull, LogIn, UserPlus } from 'lucide-react'

export default function LoginPage() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [isRegister, setIsRegister] = useState(false)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { setToken, setUser } = useStore()
  const navigate = useNavigate()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const res = isRegister
        ? await api.register(username, password)
        : await api.login(username, password)
      setToken(res.token)
      setUser(res.user)
      navigate('/')
    } catch (e: any) {
      setError(e.message)
    }
    setLoading(false)
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-dvmcp-bg">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <Skull className="w-16 h-16 text-dvmcp-accent mx-auto mb-4" />
          <h1 className="text-3xl font-bold text-white">DVMCP <span className="text-dvmcp-accent">v2.0</span></h1>
          <p className="text-gray-500 mt-2">Damn Vulnerable MCP Server</p>
          <p className="text-gray-600 text-sm mt-1">Black Hat Asia 2026 Edition</p>
        </div>
        <form onSubmit={handleSubmit} className="card space-y-4">
          <h2 className="text-xl font-semibold text-white">
            {isRegister ? 'Create Account' : 'Sign In'}
          </h2>
          {error && (
            <div className="bg-red-900/30 border border-red-800 text-red-400 text-sm rounded-lg p-3">
              {error}
            </div>
          )}
          <div>
            <label className="block text-sm text-gray-400 mb-1">Username</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full bg-dvmcp-bg border border-dvmcp-border rounded-lg px-4 py-2 text-white focus:outline-none focus:border-dvmcp-accent"
              required
            />
          </div>
          <div>
            <label className="block text-sm text-gray-400 mb-1">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full bg-dvmcp-bg border border-dvmcp-border rounded-lg px-4 py-2 text-white focus:outline-none focus:border-dvmcp-accent"
              required
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            className="btn-primary w-full flex items-center justify-center gap-2"
          >
            {loading ? 'Please wait...' : (
              <>
                {isRegister ? <UserPlus className="w-4 h-4" /> : <LogIn className="w-4 h-4" />}
                {isRegister ? 'Register' : 'Sign In'}
              </>
            )}
          </button>
          <button
            type="button"
            onClick={() => { setIsRegister(!isRegister); setError('') }}
            className="w-full text-center text-sm text-gray-500 hover:text-gray-300"
          >
            {isRegister ? 'Already have an account? Sign in' : "Don't have an account? Register"}
          </button>
        </form>
      </div>
    </div>
  )
}
