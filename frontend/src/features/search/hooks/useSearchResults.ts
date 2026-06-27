import { keepPreviousData, useQuery } from '@tanstack/react-query'
import { searchPrices, type SearchParams } from '@/api/search'
import { queryKeys } from '@/api/queryKeys'

export function useSearchResults(params: SearchParams) {
  const isEnabled = Boolean(params.query?.trim().length >= 2 && params.city_slug)

  return useQuery({
    queryKey: queryKeys.search(params),
    queryFn: () => searchPrices(params),
    enabled: isEnabled,
    staleTime: 5 * 60 * 1000,
    placeholderData: keepPreviousData,
  })
}
