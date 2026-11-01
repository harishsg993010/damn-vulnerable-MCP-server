import { useStore } from '../stores/useStore'
import ChallengeCard from './ChallengeCard'

export default function ChallengeGrid() {
  const { challenges, filter } = useStore()

  const filtered = challenges.filter((c) => {
    if (filter === 'All') return true
    if (filter === 'Easy' || filter === 'Medium' || filter === 'Hard')
      return c.difficulty === filter
    return c.category === filter
  })

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
      {filtered.map((c) => (
        <ChallengeCard key={c.id} challenge={c} />
      ))}
      {filtered.length === 0 && (
        <div className="col-span-full text-center text-gray-500 py-12">
          No challenges match the current filter.
        </div>
      )}
    </div>
  )
}
