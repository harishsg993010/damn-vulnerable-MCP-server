import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import './index.css'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import ChallengePage from './pages/Challenge'
import LeaderboardPage from './pages/Leaderboard'
import ProfilePage from './pages/Profile'
import AnalyticsPage from './pages/Analytics'
import LoginPage from './pages/Login'

class ErrorBoundary extends React.Component<
  { children: React.ReactNode },
  { hasError: boolean; errorMsg: string }
> {
  state = { hasError: false, errorMsg: '' }
  static getDerivedStateFromError(error: Error) {
    return { hasError: true, errorMsg: error?.message || String(error) }
  }
  componentDidCatch(error: Error, info: React.ErrorInfo) {
    console.error('ErrorBoundary caught:', error, info.componentStack)
  }
  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen flex items-center justify-center bg-dvmcp-bg text-white">
          <div className="text-center space-y-4 max-w-lg px-4">
            <h1 className="text-2xl font-bold">Something went wrong</h1>
            <p className="text-sm text-gray-400 font-mono break-all">{this.state.errorMsg}</p>
            <button
              onClick={() => { this.setState({ hasError: false, errorMsg: '' }); window.location.href = '/' }}
              className="px-4 py-2 bg-dvmcp-accent rounded-lg hover:opacity-90"
            >
              Reload Dashboard
            </button>
          </div>
        </div>
      )
    }
    return this.props.children
  }
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ErrorBoundary>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/" element={<Layout />}>
            <Route index element={<Dashboard />} />
            <Route path="challenge/:id" element={<ChallengePage />} />
            <Route path="leaderboard" element={<LeaderboardPage />} />
            <Route path="profile" element={<ProfilePage />} />
            <Route path="analytics" element={<AnalyticsPage />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </ErrorBoundary>
  </React.StrictMode>,
)
