import { useState } from 'react'
import { api } from '../utils/api'
import { useStore } from '../stores/useStore'
import { Flag, Loader2, CheckCircle2, XCircle } from 'lucide-react'

export default function FlagSubmission({ challengeId }: { challengeId: number }) {
  const [flag, setFlag] = useState('')
  const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle')
  const [message, setMessage] = useState('')
  const { updateChallengeStatus, setUser } = useStore()

  const submit = async () => {
    if (!flag.trim()) return
    setStatus('loading')
    try {
      const res = await api.submitFlag(challengeId, flag.trim())
      if (res.correct) {
        setStatus('success')
        setMessage(`Correct! +${res.points_awarded} points`)
        updateChallengeStatus(challengeId, 'completed')
        api.getProfile().then(setUser)
      } else {
        setStatus('error')
        setMessage(res.message || 'Incorrect flag. Try again.')
      }
    } catch (e: any) {
      setStatus('error')
      setMessage(e.message)
    }
  }

  return (
    <div className="card">
      <h3 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
        <Flag className="w-5 h-5 text-dvmcp-accent" />
        Submit Flag
      </h3>
      <div className="flex gap-2">
        <input
          type="text"
          value={flag}
          onChange={(e) => { setFlag(e.target.value); setStatus('idle') }}
          onKeyDown={(e) => e.key === 'Enter' && submit()}
          placeholder="DVMCP{...}"
          className="flex-1 bg-dvmcp-bg border border-dvmcp-border rounded-lg px-4 py-2 text-sm font-mono text-white placeholder-gray-600 focus:outline-none focus:border-dvmcp-accent"
        />
        <button onClick={submit} disabled={status === 'loading'} className="btn-primary flex items-center gap-2">
          {status === 'loading' ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Submit'}
        </button>
      </div>
      {status === 'success' && (
        <div className="mt-3 flex items-center gap-2 text-green-400 text-sm">
          <CheckCircle2 className="w-4 h-4" /> {message}
        </div>
      )}
      {status === 'error' && (
        <div className="mt-3 flex items-center gap-2 text-red-400 text-sm">
          <XCircle className="w-4 h-4" /> {message}
        </div>
      )}
    </div>
  )
}
