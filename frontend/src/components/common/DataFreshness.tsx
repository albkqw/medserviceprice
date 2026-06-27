import { cn } from '@/lib/utils'
import { getFreshnessLevel, formatRelativeDate } from '@/lib/formatters'

interface DataFreshnessProps {
  parsedAt: string
  className?: string
}

const levelStyles = {
  fresh: 'text-green-600 bg-green-50',
  aging: 'text-yellow-600 bg-yellow-50',
  stale: 'text-orange-600 bg-orange-50',
  expired: 'text-red-600 bg-red-50',
}

export function DataFreshness({ parsedAt, className }: DataFreshnessProps) {
  const level = getFreshnessLevel(parsedAt)
  const label = formatRelativeDate(parsedAt)

  return (
    <span
      className={cn(
        'inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium',
        levelStyles[level],
        className,
      )}
    >
      {level === 'expired' ? 'Устарело' : label}
    </span>
  )
}
