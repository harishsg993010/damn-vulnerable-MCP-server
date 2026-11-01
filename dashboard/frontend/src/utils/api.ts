const API_BASE = '/api'

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = localStorage.getItem('dvmcp_token')
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string> || {}),
  }
  if (token) headers['Authorization'] = `Bearer ${token}`

  const res = await fetch(`${API_BASE}${path}`, { ...options, headers })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail || 'Request failed')
  }
  return res.json()
}

export const api = {
  // Auth
  register: (username: string, password: string) =>
    request<{ token: string; user: any }>('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    }),

  login: (username: string, password: string) =>
    request<{ token: string; user: any }>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    }),

  // Challenges
  getChallenges: () => request<any[]>('/challenges'),
  getChallenge: (id: number) => request<any>(`/challenges/${id}`),
  getHint: (id: number) => request<any>(`/challenges/${id}/hint`, { method: 'POST' }),

  // Submissions
  submitFlag: (challenge_id: number, flag: string) =>
    request<any>('/submit', {
      method: 'POST',
      body: JSON.stringify({ challenge_id, flag }),
    }),

  // Leaderboard
  getLeaderboard: () => request<any[]>('/leaderboard'),

  // Analytics
  getGlobalAnalytics: () => request<any>('/analytics/global'),
  getUserAnalytics: () => request<any>('/analytics/user'),
  recordEvent: (event_type: string, challenge_id: number) =>
    request<any>('/analytics/event', {
      method: 'POST',
      body: JSON.stringify({ event_type, challenge_id }),
    }),

  // User
  getProfile: () => request<any>('/user/profile'),
  getProgress: () => request<any>('/user/progress'),

  // Server status
  getServerStatus: () => request<any>('/servers/status'),

  // Playground
  playgroundInfo: (challengeId: number) =>
    request<{ tools: any[]; resources: any[] }>(`/playground/${challengeId}/info`),

  playgroundCallTool: (challengeId: number, toolName: string, args: Record<string, any>) =>
    request<{ content: any[]; isError: boolean }>(`/playground/${challengeId}/tool`, {
      method: 'POST',
      body: JSON.stringify({ tool_name: toolName, arguments: args }),
    }),

  playgroundReadResource: (challengeId: number, uri: string) =>
    request<{ contents: any[] }>(`/playground/${challengeId}/resource`, {
      method: 'POST',
      body: JSON.stringify({ uri }),
    }),

  playgroundChat: (challengeId: number, apiKey: string, messages: any[], model: string) =>
    request<{ new_messages: any[]; usage: { input_tokens: number; output_tokens: number } }>(
      `/playground/${challengeId}/chat`,
      {
        method: 'POST',
        body: JSON.stringify({ api_key: apiKey, messages, model }),
      },
    ),

  playgroundReset: (challengeId: number) =>
    request<{ status: string; message: string }>(`/playground/${challengeId}/reset`, {
      method: 'POST',
    }),
}
