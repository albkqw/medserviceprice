import { useCallback } from 'react'
import { useSearchParams } from 'react-router-dom'
import type { SortOption } from '@/types/domain'
import { DEFAULT_SORT } from '@/lib/constants'

export interface SearchFilters {
  query: string
  city_slug: string
  min_price?: number
  max_price?: number
  category?: string
  sort: SortOption
}

export function useSearchFilters() {
  const [searchParams, setSearchParams] = useSearchParams()

  const filters: SearchFilters = {
    query: searchParams.get('q') ?? '',
    city_slug: searchParams.get('city') ?? '',
    min_price: searchParams.get('min') ? Number(searchParams.get('min')) : undefined,
    max_price: searchParams.get('max') ? Number(searchParams.get('max')) : undefined,
    category: searchParams.get('category') ?? undefined,
    sort: (searchParams.get('sort') as SortOption) ?? DEFAULT_SORT,
  }

  const setFilters = useCallback(
    (updates: Partial<SearchFilters>) => {
      setSearchParams(
        (prev) => {
          const next = new URLSearchParams(prev)
          const merged = { ...filters, ...updates }

          if (merged.query) next.set('q', merged.query)
          else next.delete('q')

          if (merged.city_slug) next.set('city', merged.city_slug)
          else next.delete('city')

          if (merged.min_price != null) next.set('min', String(merged.min_price))
          else next.delete('min')

          if (merged.max_price != null) next.set('max', String(merged.max_price))
          else next.delete('max')

          if (merged.category) next.set('category', merged.category)
          else next.delete('category')

          if (merged.sort && merged.sort !== DEFAULT_SORT) next.set('sort', merged.sort)
          else next.delete('sort')

          return next
        },
        { replace: true },
      )
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [setSearchParams, searchParams.toString()],
  )

  return { filters, setFilters }
}
