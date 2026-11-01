import { create } from 'zustand'

export interface Challenge {
  id: number
  name: string
  category: string
  difficulty: 'Easy' | 'Medium' | 'Hard'
  points: number
  port: number
  description: string
  objective: string
  hints: string[]
  status: 'not_started' | 'in_progress' | 'completed'
}

export interface User {
  id: number
  username: string
  total_points: number
  challenges_completed: number
}

export interface LeaderboardEntry {
  rank: number
  username: string
  total_points: number
  challenges_completed: number
  last_submission: string
}

interface AppState {
  user: User | null
  token: string | null
  challenges: Challenge[]
  leaderboard: LeaderboardEntry[]
  filter: string
  ws: WebSocket | null

  setUser: (user: User | null) => void
  setToken: (token: string | null) => void
  setChallenges: (challenges: Challenge[]) => void
  setLeaderboard: (lb: LeaderboardEntry[]) => void
  setFilter: (f: string) => void
  updateChallengeStatus: (id: number, status: Challenge['status']) => void
  logout: () => void
  connectWs: () => void
}

export const useStore = create<AppState>((set, get) => ({
  user: null,
  token: localStorage.getItem('dvmcp_token'),
  challenges: [],
  leaderboard: [],
  filter: 'All',
  ws: null,

  setUser: (user) => set({ user }),
  setToken: (token) => {
    if (token) localStorage.setItem('dvmcp_token', token)
    else localStorage.removeItem('dvmcp_token')
    set({ token })
  },
  setChallenges: (challenges) => set({ challenges }),
  setLeaderboard: (leaderboard) => set({ leaderboard }),
  setFilter: (filter) => set({ filter }),
  updateChallengeStatus: (id, status) =>
    set((state) => ({
      challenges: state.challenges.map((c) =>
        c.id === id ? { ...c, status } : c
      ),
    })),
  logout: () => {
    localStorage.removeItem('dvmcp_token')
    set({ user: null, token: null })
  },
  connectWs: () => {
    const existing = get().ws
    if (existing && existing.readyState <= WebSocket.OPEN) return
    const scheme = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const ws = new WebSocket(`${scheme}//${window.location.host}/ws`)
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        if (data.type === 'leaderboard_update' && Array.isArray(data.leaderboard)) {
          get().setLeaderboard(data.leaderboard)
        }
      } catch (_e) { /* ignore malformed messages */ }
    }
    ws.onclose = () => {
      set({ ws: null })
      setTimeout(() => get().connectWs(), 3000)
    }
    ws.onerror = () => ws.close()
    set({ ws })
  },
}))
