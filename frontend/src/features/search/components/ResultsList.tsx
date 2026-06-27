import { SearchX } from 'lucide-react'
import { EmptyState } from '@/components/common/EmptyState'
import { ErrorState } from '@/components/common/ErrorState'
import type { SearchResult, SortOption } from '@/types/domain'
import { ResultCard } from './ResultCard'
import { ResultCardSkeleton } from './ResultCardSkeleton'

interface ResultsListProps {
  results: SearchResult[]
  isLoading: boolean
  isError: boolean
  onRetry: () => void
  query: string
  sort: SortOption
}

function sortResults(results: SearchResult[], sort: SortOption): SearchResult[] {
  return [...results].sort((a, b) => {
    if (sort === 'price_asc') return a.price_kzt - b.price_kzt
    if (sort === 'price_desc') return b.price_kzt - a.price_kzt
    if (sort === 'date_desc')
      return new Date(b.parsed_at).getTime() - new Date(a.parsed_at).getTime()
    return 0
  })
}

export function ResultsList({
  results,
  isLoading,
  isError,
  onRetry,
  query,
  sort,
}: ResultsListProps) {
  if (isLoading) {
    return (
      <div className="flex flex-col gap-3">
        {Array.from({ length: 6 }).map((_, i) => (
          <ResultCardSkeleton key={i} />
        ))}
      </div>
    )
  }

  if (isError) {
    return (
      <ErrorState
        title="Не удалось загрузить результаты"
        description="Проверьте соединение или попробуйте снова."
        onRetry={onRetry}
      />
    )
  }

  if (results.length === 0) {
    return (
      <EmptyState
        icon={<SearchX className="h-12 w-12" />}
        title={`По запросу «${query}» ничего не найдено`}
        description="Попробуйте другое название услуги или уберите ценовой фильтр."
      />
    )
  }

  const sorted = sortResults(results, sort)

  return (
    <div className="flex flex-col gap-3">
      {sorted.map((result, i) => (
        <ResultCard key={`${result.clinic_id}-${result.service_id}-${i}`} result={result} />
      ))}
    </div>
  )
}
