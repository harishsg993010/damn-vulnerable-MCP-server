import { useState } from 'react'
import { api } from '../utils/api'
import { useStore } from '../stores/useStore'
import { Lightbulb, Lock, Coins } from 'lucide-react'

const HINT_COSTS = [10, 25, 50]

export default function HintPanel({ challengeId, hints }: { challengeId: number; hints: string[] }) {
  const [revealedHints, setRevealedHints] = useState<string[]>([])
  const [loading, setLoading] = useState(false)
  const setUser = useStore((s) => s.setUser)

  const revealNext = async () => {
    setLoading(true)
    try {
      const res = await api.getHint(challengeId)
      if (res.hints) {
        setRevealedHints(res.hints.map((h: any) => h.text))
        api.getProfile().then(setUser)
      }
    } catch {
      // ignore
    }
    setLoading(false)
  }

  const nextCost = HINT_COSTS[revealedHints.length] || 50

  return (
    <div className="card">
      <h3 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
        <Lightbulb className="w-5 h-5 text-yellow-400" />
        Hints
      </h3>
      <div className="space-y-3">
        {revealedHints.map((hint, i) => (
          <div key={i} className="bg-dvmcp-bg rounded-lg p-3 text-sm text-gray-300 border-l-2 border-yellow-400">
            <span className="text-yellow-400 font-bold text-xs">HINT {i + 1}</span>
            <p className="mt-1">{hint}</p>
          </div>
        ))}
        {revealedHints.length < 3 && (
          <button
            onClick={revealNext}
            disabled={loading}
            className="btn-secondary w-full flex items-center justify-center gap-2 text-sm"
          >
            {loading ? (
              'Revealing...'
            ) : (
              <>
                <Lock className="w-3 h-3" />
                Reveal Hint {revealedHints.length + 1}
                <span className="flex items-center gap-1 text-yellow-400">
                  <Coins className="w-3 h-3" /> -{nextCost} pts
                </span>
              </>
            )}
          </button>
        )}
      </div>
    </div>
  )
}
