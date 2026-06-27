import { useQuery } from '@tanstack/react-query'
import { getServiceSuggestions } from '@/api/services'
import { queryKeys } from '@/api/queryKeys'
import { useDebounce } from '@/hooks/useDebounce'
import { AUTOCOMPLETE_MIN_CHARS, DEBOUNCE_MS } from '@/lib/constants'

export function useServiceSuggestions(query: string) {
  const debouncedQuery = useDebounce(query, DEBOUNCE_MS)
  const isEnabled = debouncedQuery.trim().length >= AUTOCOMPLETE_MIN_CHARS

  return useQuery({
    queryKey: queryKeys.suggestions(debouncedQuery),
    queryFn: () => getServiceSuggestions(debouncedQuery),
    enabled: isEnabled,
    staleTime: 30 * 60 * 1000,
  })
}
